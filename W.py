import streamlit as st
import requests
from datetime import date, timedelta

# ==========================================
# 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 날씨 예보",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ 서울 날씨 예보")
st.write("날짜를 선택하면 해당 날짜의 날씨를 확인할 수 있습니다.")

# ==========================================
# 서울 위치
# ==========================================

LATITUDE = 37.5665
LONGITUDE = 126.9780

# Open-Meteo API
API_URL = "https://api.open-meteo.com/v1/forecast"

# ==========================================
# 날짜 선택
# ==========================================

today = date.today()

selected_date = st.date_input(
    "📅 날짜를 선택하세요",
    value=today,
    min_value=today,
    max_value=today + timedelta(days=15)
)

# ==========================================
# 날씨 코드 변환
# ==========================================

def weather_text(code):

    code = int(code)

    weather = {
        0: "☀️ 맑음",
        1: "🌤️ 대체로 맑음",
        2: "⛅ 부분적으로 흐림",
        3: "☁️ 흐림",
        45: "🌫️ 안개",
        48: "🌫️ 서리 안개",
        51: "🌦️ 약한 이슬비",
        53: "🌦️ 이슬비",
        55: "🌧️ 강한 이슬비",
        61: "🌧️ 약한 비",
        63: "🌧️ 비",
        65: "🌧️ 강한 비",
        71: "🌨️ 약한 눈",
        73: "❄️ 눈",
        75: "❄️ 강한 눈",
        80: "🌦️ 약한 소나기",
        81: "🌦️ 소나기",
        82: "🌧️ 강한 소나기",
        95: "⛈️ 뇌우",
        96: "⛈️ 우박을 동반한 뇌우",
        99: "⛈️ 강한 뇌우"
    }

    return weather.get(code, "❓ 알 수 없음")


# ==========================================
# 날씨 조회
# ==========================================

def get_weather():

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum"
        ],

        "timezone": "Asia/Seoul",
        "forecast_days": 16
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# 조회 버튼
# ==========================================

if st.button("🔍 날씨 조회", use_container_width=True):

    try:

        with st.spinner("날씨 정보를 가져오는 중..."):

            data = get_weather()

        dates = data["daily"]["time"]

        target = selected_date.strftime("%Y-%m-%d")

        if target not in dates:

            st.error("선택한 날짜의 날씨 데이터를 찾을 수 없습니다.")

        else:

            index = dates.index(target)

            weather_code = data["daily"]["weather_code"][index]

            max_temp = data["daily"]["temperature_2m_max"][index]

            min_temp = data["daily"]["temperature_2m_min"][index]

            rain_probability = data["daily"][
                "precipitation_probability_max"
            ][index]

            precipitation = data["daily"][
                "precipitation_sum"
            ][index]

            # ==================================
            # 결과
            # ==================================

            st.success(
                f"📅 {selected_date.strftime('%Y년 %m월 %d일')} "
                "서울 날씨"
            )

            st.markdown(
                f"# {weather_text(weather_code)}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "🌡️ 최고기온",
                    f"{max_temp} °C"
                )

                st.metric(
                    "🌧️ 강수확률",
                    f"{rain_probability}%"
                )

            with col2:

                st.metric(
                    "🥶 최저기온",
                    f"{min_temp} °C"
                )

                st.metric(
                    "💧 예상 강수량",
                    f"{precipitation} mm"
                )

            st.divider()

            st.subheader("📋 날씨 정보")

            st.write(
                f"**날씨:** {weather_text(weather_code)}"
            )

            st.write(
                f"**최고기온:** {max_temp} °C"
            )

            st.write(
                f"**최저기온:** {min_temp} °C"
            )

            st.write(
                f"**강수확률:** {rain_probability}%"
            )

            st.write(
                f"**예상 강수량:** {precipitation} mm"
            )

    except requests.exceptions.RequestException as e:

        st.error(
            f"❌ 날씨 API 연결 오류가 발생했습니다.\n\n{e}"
        )

    except Exception as e:

        st.error(
            f"❌ 오류가 발생했습니다.\n\n{e}"
        )
