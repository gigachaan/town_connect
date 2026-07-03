import streamlit as st
import pandas as pd
import numpy as np

# ------------------------------------------------
# 1. 페이지 기본 설정 및 데이터 저장소(session_state) 초기화
# ------------------------------------------------
st.set_page_config(page_title="마을잇다 대시보드", layout="wide")

# 앱이 재실행되어도 데이터가 날아가지 않게 빈 데이터프레임을 'session_state'에 만들어 둡니다.
if 'order_data' not in st.session_state:
    st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도"])

# 마을별 임의의 위경도 (지도 표시용)
location_dict = {
    "A마을(산간)": [37.8, 128.8],
    "B마을(도서)": [37.5, 126.8],
    "C마을(농촌)": [36.5, 127.5]
}

# ------------------------------------------------
# 2. 사이드바(Sidebar) 메뉴 구성
# ------------------------------------------------
st.sidebar.title("🏡 마을잇다 메뉴")
menu = st.sidebar.radio(
    "이동할 페이지를 선택하세요:",
    ("1. 생필품 수요 신청", "2. 누적 데이터 분석", "3. 취약지역 현황 지도")
)

# ------------------------------------------------
# 3. 선택한 메뉴에 따라 다르게 보여줄 화면(if 조건문)
# ------------------------------------------------

if menu == "1. 생필품 수요 신청":
    st.header("📝 생필품 수요 신청 (마을 관리자용)")
    st.write("마을에 필요한 물품을 플랫폼에 등록합니다.")
    
    # 폼 입력
    village = st.selectbox("마을을 선택하세요", ["A마을(산간)", "B마을(도서)", "C마을(농촌)"])
    item = st.selectbox("필요한 품목", ["생수 (박스)", "쌀 (10kg)", "상비약 세트", "신선식품"])
    amount = st.slider("필요 수량", 1, 50, 5)
    
    if st.button("플랫폼에 신청하기"):
        # 1. 입력받은 데이터를 딕셔너리로 묶기
        new_data = {
            "마을명": village,
            "품목": item,
            "수량": amount,
            "위도": location_dict[village][0],
            "경도": location_dict[village][1]
        }
        # 2. session_state에 있는 데이터프레임에 새로운 행 추가하기
        st.session_state['order_data'] = pd.concat(
            [st.session_state['order_data'], pd.DataFrame([new_data])], 
            ignore_index=True
        )
        st.success(f"✅ {village}에서 '{item}' {amount}개가 성공적으로 신청되었습니다!")
        
    # [확인용] 현재까지 누적된 데이터 보기
    with st.expander("현재까지 신청된 전체 내역 보기"):
        st.dataframe(st.session_state['order_data'])

elif menu == "2. 누적 데이터 분석":
    st.header("📊 누적 데이터 분석 (운영자 대시보드)")
    
    df = st.session_state['order_data']
    
    if df.empty:
        st.info("아직 신청된 데이터가 없습니다. 왼쪽 메뉴의 '수요 신청'에서 데이터를 먼저 입력해 주세요.")
    else:
        # 탭(Tabs)을 활용해 좁은 화면을 효율적으로 분리합니다.
        tab1, tab2 = st.tabs(["마을별 신청 현황", "품목별 수요 순위"])
        
        with tab1:
            st.write("각 마을에서 어떤 물품을 얼마나 신청했는지 확인합니다.")
            # 마을과 품목을 그룹화(groupby)하여 그래프로 그리기
            village_grouped = df.groupby(["마을명", "품목"])["수량"].sum().unstack().fillna(0)
            st.bar_chart(village_grouped)
            
        with tab2:
            st.write("전체 지역에서 가장 많이 필요한 품목 순위입니다.")
            # 품목별로 수량만 그룹화
            item_grouped = df.groupby("품목")["수량"].sum()
            st.bar_chart(item_grouped)

elif menu == "3. 취약지역 현황 지도":
    st.header("🗺️ 취약지역 실시간 현황")
    
    df = st.session_state['order_data']
    
    if df.empty:
        st.info("데이터가 없어 지도를 표시할 수 없습니다.")
    else:
        st.write("물품 신청이 발생한 마을의 위치를 지도에 시각화합니다.")
        # 스트림릿 내장 지도는 무조건 컬럼명이 'lat', 'lon'이어야 동작합니다.
        map_df = df[["위도", "경도"]].copy()
        map_df.columns = ["lat", "lon"]
        st.map(map_df)