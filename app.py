import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="마을잇다 대시보드", layout="wide")

if 'order_data' not in st.session_state:
    st.session_state['order_data'] = pd.DataFrame(columns=["마을명", "품목", "수량", "위도", "경도", "상태"])

location_dict = {
    "A마을(산간)": [37.8, 128.8], "B마을(도서)": [37.5, 126.8], "C마을(농촌)": [36.5, 127.5]
}

st.sidebar.title("🏡 마을잇다 플랫폼")
user_mode = st.sidebar.radio("접속:", ("마을 관리자", "운영자(관리자)"))

menu = None
if user_mode == "마을 관리자":
    menu = st.sidebar.radio("메뉴:", ("1. 생필품 수요 신청",))
else:
    if st.sidebar.text_input("비밀번호:", type="password") == "1234":
        menu = st.sidebar.radio("메뉴:", ("2. 통합 대시보드", "3. 취약지역 지도", "4. 배송 매칭 관리"))

# [기능 1] 마을 관리자: 상태값 추가 (위험/정상)
if menu == "1. 생필품 수요 신청":
    st.header("📝 생필품 수요 신청")
    village = st.selectbox("마을", list(location_dict.keys()))
    item = st.selectbox("품목", ["생수", "쌀", "상비약", "신선식품"])
    amount = st.slider("수량", 1, 50, 10)
    # 수량이 30 이상이면 위험으로 간주
    status = "🚨위험" if amount > 30 else "✅정상"
    
    if st.button("신청하기"):
        new_data = {"마을명": village, "품목": item, "수량": amount, "위도": location_dict[village][0], "경도": location_dict[village][1], "상태": status}
        st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new_data])], ignore_index=True)
        st.success(f"{village} 신청 완료! ({status})")

# [기능 2] 통합 대시보드: 데이터 필터링 추가
elif menu == "2. 통합 대시보드":
    st.header("📊 통합 대시보드")
    df = st.session_state['order_data']
    if not df.empty:
        # 사이드바 필터링 기능
        filter_village = st.sidebar.multiselect("마을 필터:", df['마을명'].unique())
        if filter_village:
            df = df[df['마을명'].isin(filter_village)]
        
        st.metric("총 신청", f"{len(df)}건")
        st.dataframe(df)
        
        # CSV 다운로드
        st.download_button("📥 데이터 다운로드", df.to_csv(index=False), "data.csv")

# [기능 3] 배송 매칭 관리: 위험 마을 자동 매칭 시뮬레이션
elif menu == "4. 배송 매칭 관리":
    st.header("🚚 배송 매칭/공급처 연결")
    df = st.session_state['order_data']
    danger_df = df[df['상태'] == "🚨위험"]
    
    if not danger_df.empty:
        st.error(f"🚨 긴급 지원 필요 마을: {danger_df['마을명'].unique()}")
        for idx, row in danger_df.iterrows():
            with st.expander(f"{row['마을명']} 지원 배차"):
                st.write(f"품목: {row['품목']} / 수량: {row['수량']}")
                if st.button(f"배송 승인 ({row['마을명']})", key=idx):
                    st.success("배송차량 매칭 완료!")
    else:
        st.success("현재 긴급 지원이 필요한 마을이 없습니다.")