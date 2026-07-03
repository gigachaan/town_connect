import streamlit as st
import pandas as pd

st.set_page_config(page_title="마을잇다 고도화", layout="wide")

# 세션 데이터 초기화
if 'order_data' not in st.session_state:
    st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도", "상태"])

# 지도 색상 매핑 함수
def get_color(status):
    return "red" if status == "🚨위험" else "blue"

# 사이드바 설정
st.sidebar.title("🚀 마을잇다 관리자")
user_mode = st.sidebar.radio("모드:", ("마을 관리자", "운영자(관리자)"))

# 운영자 모드 인증
if user_mode == "운영자(관리자)":
    if st.sidebar.text_input("비밀번호:", type="password") != "1234":
        st.sidebar.error("인증 실패")
        st.stop()
    menu = st.sidebar.radio("운영 메뉴:", ("통합 분석", "취약지역 지도", "실시간 관제 로그"))
else:
    menu = "수요 신청"

# 화면 출력 로직
if menu == "수요 신청":
    st.header("📝 생필품 수요 신청")
    v = st.selectbox("마을", ["A마을", "B마을", "C마을"])
    i = st.selectbox("품목", ["쌀", "생수", "상비약"])
    q = st.slider("수량", 1, 50, 10)
    if st.button("신청하기"):
        loc = {"A마을": [37.8, 128.8], "B마을": [37.5, 126.8], "C마을": [36.5, 127.5]}[v]
        new = {"마을명": v, "품목": i, "수량": q, "위도": loc[0], "경도": loc[1], "상태": "🚨위험" if q > 30 else "✅정상"}
        st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new])], ignore_index=True)
        st.success("데이터 접수 완료")

elif menu == "통합 분석":
    st.header("📊 통합 데이터 분석")
    df = st.session_state['order_data']
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.bar_chart(df.groupby("품목")["수량"].sum())
        col2.dataframe(df)
        st.info(f"💡 AI 분석: '{df.groupby('품목')['수량'].sum().idxmax()}' 우선 지원 필요")

elif menu == "취약지역 지도":
    st.header("🗺️ 취약지역 위치 파악")
    df = st.session_state['order_data']
    if not df.empty:
        df['color'] = df['상태'].apply(get_color)
        st.map(df, latitude='위도', longitude='경도', color='color')

elif menu == "실시간 관제 로그":
    st.header("📜 관제 시스템 로그")
    df = st.session_state['order_data']
    log_text = "\n".join([f"[{m}] {i} - {s}" for m, i, s in zip(df['마을명'], df['품목'], df['상태'])])
    st.code(log_text if log_text else "로그 없음", language="text")
    if st.button("데이터 초기화"):
        st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도", "상태"])
        st.rerun()