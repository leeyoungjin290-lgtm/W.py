import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="날씨 예보",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ 기상청 날씨 예보")
st.write("날짜를 선택하면 서울의 날씨 예보를 보여줍니다.")

# ==========================================
# API 키
# ==========================================

try:
    API_KEY = st.secrets["KMA_API_KEY"]
except Exception:
    API_KEY = ""

# ==========================================
# 서울 격자 좌표
# ==========================================

NX = 60
NY = 127

# ==========================================
# 날짜 선택
# ==========================================

today = date.today()

selected_date = st.date_input(
    "📅 날짜를 선택하세요",
    value=today,
    min_value=today,
    max_value=today + timedelta(days=5)
)

# ==========================================
# 가장 최근 기상청 발표시간 계산
# ==========================================

def get_base_time():

    now = datetime.now()

    # 기상청 단기예보 발표시간
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    # 현재 시간에서 가장 최근 발표시간 찾기
    for hour in reversed(base_hours):

        if now.hour > hour or (
            now.hour == hour and now.minute >= 10
        ):
            return (
                now.strftime("%Y%m%d"),
                f"{hour:02d}00"
            )

    # 오늘 첫 발표 전이면 어제 23시 발표 사용
    yesterday = now - timedelta(days=1)

    return (
        yesterday.strftime("%Y%m%d"),
        "2300"
    )


# ==========================================
# 기상청 API 호출
# ==========================================

def get_weather(target_date):

    if not API_KEY:
        return None, "기상청 API 인증키가 없습니다."

    base_date, base_time = get_base_time()

    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/"
        "VilageFcstInfoService_2.0/getVilageFcst"
    )

    params = {
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": NX,
        "ny": NY,
        "authKey": API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        response_data = data.get("response", {})
        header = response_data.get("header", {})

        # API 오류 확인
        if header.get("resultCode") != "00":
            return None, (
                "기상청 API 오류: "
                + str(header.get("resultMsg", "알 수 없는 오류"))
            )

        body = response_data.get("body", {})
        items = body.get("items", {}).get("item", [])

        target = target_date.strftime("%Y%m%d")

        result = {}

        for item in items:

            if item["fcstDate"] != target:
                continue

            time = item["fcstTime"]
            category = item["category"]
            value = item["fcstValue"]

            if time not in result:
                result[time] = {}

            result[time][category] = value

        if not result:
            return None, (
                "선택한 날짜의 예보가 없습니다.\n"
                "단기예보에서 제공하는 날짜인지 확인해주세요."
            )

        return result, None

    except requests.exceptions.RequestException as e:

        return None, f"인터넷/API 요청 오류: {e}"

    except ValueError:

        return None, (
            "기상청 API에서 JSON 데이터를 받지 못했습니다.\n"
            "인증키가 올바른지 확인해주세요."
        )

    except Exception as e:

        return None, f"오류가 발생했습니다: {e}"


# ==========================================
# 날씨 표시용 함수
# ==========================================

def sky_text(value):

    if value == "1":
        return "☀️ 맑음"

    if value == "3":
        return "🌤️ 구름많음"

    if value == "4":
        return "☁️ 흐림"

    return "알 수 없음"


def rain_text(value):

    if value == "0":
        return "없음"

    if value == "1":
        return "🌧️ 비"

    if value == "2":
        return "🌨️ 비/눈"

    if value == "3":
        return "❄️ 눈"

    if value == "4":
        return "🌦️ 소나기"

    return "알 수 없음"


# ==========================================
# 조회 버튼
# ==========================================

if st.button("🔍 날씨 조회", use_container_width=True):

    if not API_KEY:

        st.error(
            "기상청 API 인증키가 없습니다.\n\n"
            "Streamlit Cloud의 Secrets에 "
            "`KMA_API_KEY`를 등록해주세요."
        )

    else:

        with st.spinner("기상청에서 예보를 가져오는 중..."):

            weather, error = get_weather(selected_date)

        if error:

            st.error(error)

        else:

            st.success(
                f"{selected_date.strftime('%Y년 %m월 %d일')} "
                "서울 날씨 예보"
            )

            # 시간순으로 표시
            for time in sorted(weather.keys()):

                data = weather[time]

                hour = time[:2]

                temperature = data.get("TMP", "-")
                sky = data.get("SKY", "-")
                rain_type = data.get("PTY", "0")
                rain_probability = data.get("POP", "-")
                humidity = data.get("REH", "-")
                wind = data.get("WSD", "-")

                st.markdown(
                    f"""
                    ## 🕐 {hour}시

                    🌡️ **기온:** {temperature} ℃

                    ☁️ **날씨:** {sky_text(sky)}

                    🌧️ **강수 형태:** {rain_text(rain_type)}

                    💧 **강수확률:** {rain_probability} %

                    💦 **습도:** {humidity} %

                    💨 **풍속:** {wind} m/s
                    """
                )

                st.divider()
