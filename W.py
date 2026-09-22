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

if st
