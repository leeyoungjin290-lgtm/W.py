import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="날씨 예보",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ 날씨 예보")
st.write("날짜를 선택하면 서울의 날씨 예보를 확인할 수 있습니다.")

# ==========================================
# API 설정
# ==========================================

try:
    API_KEY = st.secrets["KMA_API_KEY"]
except:
    API_KEY = ""

# 서울 격자 좌표
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
# 기상청 API 요청
# ==========================================

def get_weather(target_date):

    if not API_KEY:
        return None, "API 키가 없습니다."

    now = datetime.now()

    # 기상청 단기예보 발표시간
    base_times = [2300, 2000, 1700, 1400, 1100, 800, 500, 200]

    # 현재 시간보다 이전에 발표된 가장 최근 발표시간 찾기
    possible_times = []

    for bt in base_times:

        hour = bt // 100
        minute = bt % 100

        base_datetime = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        # 아직 발표되지 않은 시간은 제외
        if base_datetime <= now:
            possible_times.append((bt, base_datetime))

    # 오늘 발표자료가 없다면 어제 23시 자료 사용
    if possible_times:
        base_time = possible_times[0][0]
        base_date = now.strftime("%Y%m%d")
    else:
        base_time = 2300
        base_date = (now - timedelta(days=1)).strftime("%Y%m%d")

    url = (
        "https://apihub.kma.go.kr/api/typ02/openApi/"
        "VilageFcstInfoService_2.0/getVilageFcst"
    )

    params = {
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": f"{base_time:04d}",
        "nx": NX,
        "ny": NY,
        "authKey": API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # API 오류 확인
        header = data.get("response", {}).get("header", {})

        if header.get("resultCode") != "00":
            return None, header.get(
                "resultMsg",
                "기상청 API 오류"
            )

        items = data["response"]["body"]["items"]["item"]

        target = target_date.strftime("%Y%m%d")

        weather = {}

        for item in items:

           
