import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="기상청 날씨 예보",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ 기상청 날씨 예보")
st.write("날짜를 선택하면 서울의 날씨 예보를 확인할 수 있습니다.")

# ==========================================
# 기상청 API
# ==========================================

API_URL = (
    "https://apihub.kma.go.kr/api/typ02/openApi/"
    "VilageFcstInfoService_2.0/getVilageFcst"
)

# 서울 격자 좌표
NX = 60
NY = 127

# ==========================================
# API 인증키 입력
# ==========================================

API_KEY = st.text_input(
    "🔑 기상청 API 인증키",
    type="password",
    placeholder="기상청에서 발급받은 인증키를 입력하세요"
)

# ==========================================
# 날짜 선택
# ==========================================

today = date.today()

selected_date = st.date_input(
    "📅 예보 날짜",
    value=today,
    min_value=today,
    max_value=today + timedelta(days=5)
)

# ==========================================
# 기상청 발표시간
# ==========================================

def get_base_time():

    now = datetime.now()

    base_times = [
        (2, "0200"),
        (5, "0500"),
        (8, "0800"),
        (11, "1100"),
        (14, "1400"),
        (17, "1700"),
        (20, "2000"),
        (23, "2300")
    ]

    for hour, base_time in reversed(base_times):

        if now.hour > hour or (
            now.hour == hour and now.minute >= 10
        ):
            return now.strftime("%Y%m%d"), base_time

    yesterday = now - timedelta(days=1)

    return yesterday.strftime("%Y%m%d"), "2300"


# ==========================================
# 날씨 API 요청
# ==========================================

def get_weather():

    base_date, base_time = get_base_time()

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

    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# 날씨 상태 변환
# ==========================================

def get_sky(value):

    if value == "1":
        return "☀️ 맑음"

    if value == "3":
        return "🌤️ 구름많음"

    if value == "4":
        return "☁️ 흐림"

    return "-"


def get_rain(value):

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

    return "-"


# ==========================================
# 날씨 조회 버튼
# ==========================================

if st.button("🔍 날씨 조회", use_container_width=True):

    if not API_KEY.strip():

        st.error("⚠️ 기상청 API 인증키를 입력해주세요.")

    else:

        with st.spinner("기상청에서 날씨를 가져오는 중..."):

            try:

                result = get_weather()

                response_data = result.get(
                    "response",
                    {}
                )

                header = response_data.get(
                    "header",
                    {}
                )

                # ------------------------------
                # API 오류 확인
                # ------------------------------

                if header.get("resultCode") != "00":

                    st.error(
                        "기상청 API 오류\n\n"
                        + str(
                            header.get(
                                "resultMsg",
                                "알 수 없는 오류"
                            )
                        )
                    )

                else:

                    items = (
                        response_data
                        .get("body", {})
                        .get("items", {})
                        .get("item", [])
                    )

                    target_date = (
                        selected_date.strftime("%Y%m%d")
                    )

                    weather = {}

                    # ------------------------------
                    # 선택한 날짜 데이터만 추출
                    # ------------------------------

                    for item in items:

                        if item["fcstDate"] != target_date:
                            continue

                        time = item["fcstTime"]
                        category = item["category"]
                        value = item["fcstValue"]

                        if time not in weather:
                            weather[time] = {}

                        weather[time][category] = value

                    # ------------------------------
                    # 데이터가 없는 경우
                    # ------------------------------

                    if not weather:

                        st.warning(
                            "선택한 날짜의 예보 데이터가 없습니다."
                        )

                    else:

                        st.success(
                            f"📅 {selected_date.strftime('%Y년 %m월 %d일')} "
                            "서울 날씨 예보"
                        )

                        # ------------------------------
                        # 시간별 날씨
                        # ------------------------------

                        for time in sorted(weather):

                            data = weather[time]

                            hour = time[:2]

                            temperature = data.get(
                                "TMP",
                                "-"
                            )

                            sky = data.get(
                                "SKY",
                                "-"
                            )

                            rain_type = data.get(
                                "PTY",
                                "0"
                            )

                            rain_probability = data.get(
                                "POP",
                                "-"
                            )

                            humidity = data.get(
                                "REH",
                                "-"
                            )

                            wind = data.get(
                                "WSD",
                                "-"
                            )

                            st.markdown(
                                f"## 🕐 {hour}시"
                            )

                            col1, col2 = st.columns(2)

                            with col1:

                                st.metric(
                                    "🌡️ 기온",
                                    f"{temperature} ℃"
                                )

                                st.write(
                                    f"☁️ **날씨:** "
                                    f"{get_sky(sky)}"
                                )

                                st.write(
                                    f"🌧️ **강수:** "
                                    f"{get_rain(rain_type)}"
                                )

                            with col2:

                                st.metric(
                                    "💧 강수확률",
                                    f"{rain_probability}%"
                                )

                                st.write(
                                    f"💦 **습도:** "
                                    f"{humidity}%"
                                )

                                st.write(
                                    f"💨 **풍속:** "
                                    f"{wind} m/s"
                                )

                            st.divider()

            except requests.exceptions.RequestException as e:

                st.error(
                    "❌ 기상청 API에 연결할 수 없습니다.\n\n"
                    f"{e}"
                )

            except Exception as e:

                st.error(
                    "❌ 오류가 발생했습니다.\n\n"
                    f"{e}"
              )
