import streamlit as st
import pandas as pd
import pydeck as pdk

# 1. 페이지 설정 및 세션 데이터 초기화
st.set_page_config(page_title="마을잇다 플랫폼", layout="wide")

if 'order_data' not in st.session_state:
    st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도", "상태"])

# 관리자 계정별 매칭 (마을별 권한)
admin_auth = {"admin_A": "A마을", "admin_B": "B마을", "admin_C": "C마을"}
loc_dict = {"A마을": [37.8, 128.8], "B마을": [37.5, 126.8], "C마을": [36.5, 127.5]}

# 2. 사이드바 및 인증
st.sidebar.title("🚀 마을잇다 제어판")
user_mode = st.sidebar.radio("모드:", ("마을 관리자", "운영자(관리자)"))

menu = None
my_village = None

if user_mode == "마을 관리자":
    login_id = st.sidebar.text_input("관리자 ID (예: admin_A):")
    if login_id in admin_auth:
        my_village = admin_auth[login_id]
        menu = "수요 신청"
    else:
        st.sidebar.error("유효한 ID를 입력하세요.")
else:
    if st.sidebar.text_input("운영자 비번:", type="password") == "1234":
        menu = st.sidebar.radio("운영 메뉴:", ("통합 분석", "취약지역 지도", "배송 매칭 관리", "실시간 로그"))
    else:
        st.sidebar.warning("비밀번호 필요")

# 3. 기능 로직
if menu == "수요 신청":
    st.header(f"📝 {my_village} 전용 수요 신청")
    item = st.selectbox("품목", ["쌀", "생수", "상비약", "밀키트", "기저귀", "신선식품"])
    amount = st.slider("수량", 1, 50, 10)
    
    if st.button("신청하기"):
        loc = loc_dict[my_village]
        new = {"마을명": my_village, "품목": item, "수량": amount, "위도": loc[0], "경도": loc[1], "상태": "🚨위험" if amount > 30 else "✅정상"}
        st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new])], ignore_index=True)
        st.success(f"{my_village} 신청 완료!")

elif menu == "통합 분석":
    st.header("📊 통합 데이터 분석")
    df = st.session_state['order_data']
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("총 신청 건수", f"{len(df)}건")
        col2.bar_chart(df.groupby("품목")["수량"].sum())
        st.download_button("📥 데이터 CSV 다운로드", df.to_csv(index=False), "data.csv")

elif menu == "취약지역 지도":
    st.header("🗺️ 상세 지도 (마커 클릭 정보 표시)")
    df = st.session_state['order_data']
    if not df.empty:
        st.pydeck_chart(pdk.Deck(
            layers=[pdk.Layer("ScatterplotLayer", df, get_position='[경도, 위도]', 
                              get_color='[255, 0, 0] if 상태 == "🚨위험" else [0, 0, 255]',
                              get_radius=5000, pickable=True)],
            initial_view_state=pdk.ViewState(latitude=37.2, longitude=127.5, zoom=7),
            tooltip={"text": "마을: {마을명}\n품목: {품목}\n상태: {상태}"}
        ))

elif menu == "배송 매칭 관리":
    st.header("🚚 긴급 배송 매칭")
    df = st.session_state['order_data']
    danger = df[df['상태'] == "🚨위험"]
    if not danger.empty:
        for idx, row in danger.iterrows():
            if st.button(f"배송 승인: {row['마을명']} ({row['품목']})", key=idx):
                st.success("배송 매칭 완료!")
    else:
        st.info("긴급 지원이 필요한 마을이 없습니다.")

elif menu == "실시간 로그":
    st.header("📜 시스템 운영 로그")
    df = st.session_state['order_data']
    log_data = "\n".join([f"[{m}] {i} {s}" for m, i, s in zip(df['마을명'], df['품목'], df['상태'])])
    st.code(log_data if log_data else "로그 없음", language="text")