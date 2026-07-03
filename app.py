import streamlit as st
import pandas as pd
import numpy as np

# ------------------------------------------------
# 1. 페이지 설정 및 데이터 저장소 초기화
# ------------------------------------------------
st.set_page_config(page_title="마을잇다 대시보드", layout="wide")

if 'order_data' not in st.session_state:
    st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도"])

location_dict = {
    "A마을(산간)": [37.8, 128.8],
    "B마을(도서)": [37.5, 126.8],
    "C마을(농촌)": [36.5, 127.5]
}

# ------------------------------------------------
# 2. 사이드바: 모드 선택 및 보안 로직
# ------------------------------------------------
st.sidebar.title("🏡 마을잇다 플랫폼")
user_mode = st.sidebar.radio("접속 타입을 선택하세요:", ("마을 관리자", "운영자(관리자)"))
st.sidebar.divider()

menu = None
if user_mode == "마을 관리자":
    menu = st.sidebar.radio("메뉴:", ("1. 생필품 수요 신청",))
else:
    # 운영자 모드 진입 시 비밀번호 확인
    password = st.sidebar.text_input("관리자 비밀번호를 입력하세요:", type="password")
    if password == "1234":
        menu = st.sidebar.radio("메뉴:", ("2. 누적 데이터 분석", "3. 취약지역 현황 지도"))
    else:
        st.sidebar.warning("비밀번호를 입력하면 메뉴가 나타납니다.")

# ------------------------------------------------
# 3. 모드별/메뉴별 화면 로직
# ------------------------------------------------

# [공통] 마을 관리자 화면
if menu == "1. 생필품 수요 신청":
    st.header("📝 생필품 수요 신청 (마을 관리자용)")
    
    village = st.selectbox("마을을 선택하세요", list(location_dict.keys()))
    item = st.selectbox("필요한 품목", ["생수 (박스)", "쌀 (10kg)", "상비약 세트", "신선식품"])
    amount = st.slider("필요 수량", 1, 50, 5)
    
    if st.button("플랫폼에 신청하기"):
        new_data = {
            "마을명": village, "품목": item, "수량": amount,
            "위도": location_dict[village][0], "경도": location_dict[village][1]
        }
        st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new_data])], ignore_index=True)
        st.success(f"✅ {village}에서 '{item}' {amount}개가 성공적으로 신청되었습니다!")

# [운영자] 누적 데이터 분석
elif menu == "2. 누적 데이터 분석":
    st.header("📊 운영자용 통합 대시보드")
    df = st.session_state['order_data']
    
    if df.empty:
        st.info("아직 신청된 데이터가 없습니다.")
    else:
        # 핵심 지표 카드
        col1, col2, col3 = st.columns(3)
        col1.metric("총 신청 건수", f"{len(df)}건")
        col2.metric("총 물품 수량", f"{df['수량'].sum()}개")
        col3.metric("참여 마을 수", f"{df['마을명'].nunique()}개")
        
        st.divider()

        # 데이터 다운로드 버튼 (CSV)
        csv = df.to_csv(index=False).encode('utf-8-sig') # 한글 깨짐 방지
        st.download_button(
            label="📥 분석 데이터 CSV 다운로드",
            data=csv,
            file_name="마을잇다_데이터.csv",
            mime="text/csv"
        )

        # 탭 차트
        tab1, tab2 = st.tabs(["마을별 신청 현황", "품목별 수요 순위"])
        with tab1:
            st.bar_chart(df.groupby(["마을명", "품목"])["수량"].sum().unstack().fillna(0))
        with tab2:
            st.bar_chart(df.groupby("품목")["수량"].sum())

# [운영자] 지도 현황
elif menu == "3. 취약지역 현황 지도":
    st.header("🗺️ 취약지역 실시간 현황")
    df = st.session_state['order_data']
    if df.empty:
        st.info("데이터가 없습니다.")
    else:
        map_df = df[["위도", "경도"]].copy()
        map_df.columns = ["lat", "lon"]
        st.map(map_df)