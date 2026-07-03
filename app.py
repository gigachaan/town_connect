import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

# 1. 페이지 설정 및 디자인(CSS)
st.set_page_config(page_title="마을잇다 관제센터", page_icon="🚚", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 버튼 스타일 살짝 다듬기 */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 데이터 및 초기 목업(Mock) 데이터 설정
# [디벨롭] 마을 5곳으로 확장 및 현실적인 물품 리스트로 변경
loc_dict = {
    "A마을(산간)": [37.8, 128.8], "B마을(도서)": [37.5, 126.8], 
    "C마을(농촌)": [36.5, 127.5], "D마을(해안)": [37.6, 129.0], 
    "E마을(도심)": [37.5, 127.0]
}
admin_auth = {
    "admin_A": "A마을(산간)", "admin_B": "B마을(도서)", 
    "admin_C": "C마을(농촌)", "admin_D": "D마을(해안)", 
    "admin_E": "E마을(도심)"
}

if 'order_data' not in st.session_state:
    initial_data = [
        {"마을명": "A마을(산간)", "품목": "생수", "수량": 45, "위도": 37.8, "경도": 128.8, "상태": "🚨위험", "배송": "대기중"},
        {"마을명": "B마을(도서)", "품목": "상비약", "수량": 15, "위도": 37.5, "경도": 126.8, "상태": "✅정상", "배송": "대기중"},
        {"마을명": "D마을(해안)", "품목": "재난구호키트", "수량": 35, "위도": 37.6, "경도": 129.0, "상태": "🚨위험", "배송": "대기중"}
    ]
    st.session_state['order_data'] = pd.DataFrame(initial_data)

# 3. 사이드바 및 로그인 (버튼 추가)
st.sidebar.title("🚚 마을잇다 플랫폼")
user_mode = st.sidebar.radio("접속 권한:", ("마을 관리자", "운영자(관제센터)"))
st.sidebar.divider()

menu = None
my_village = None

if user_mode == "마을 관리자":
    login_id = st.sidebar.text_input("🔑 관리자 ID (예: admin_A):")
    login_btn = st.sidebar.button("로그인", use_container_width=True) # [디벨롭] 직관적인 로그인 버튼 추가
    
    if login_id in admin_auth:
        my_village = admin_auth[login_id]
        menu = "수요 신청"
        if login_btn:
            st.sidebar.success(f"{my_village} 인증 완료")
    elif login_btn and login_id not in admin_auth:
        st.sidebar.error("유효한 ID가 아닙니다.")
else:
    op_pw = st.sidebar.text_input("🔐 관제센터 비번 (1234):", type="password")
    op_login_btn = st.sidebar.button("로그인", use_container_width=True)
    
    if op_pw == "1234":
        menu = st.sidebar.radio("관제 메뉴:", ("📊 통합 관제 보드", "🗺️ 3D 취약 지도", "🚚 지능형 배송 매칭"))
    elif op_login_btn:
        st.sidebar.warning("보안 인가가 필요합니다.")

# 4. 기능 로직
if menu == "수요 신청":
    st.header(f"📦 {my_village} 전용 수요 신청")
    st.caption("재난 및 긴급 상황 발생 시 필요한 물품을 관제센터로 요청합니다.")
    
    with st.container(border=True):
        # [디벨롭] 기저귀 삭제, 공공재 성격의 품목으로 리뉴얼
        item = st.selectbox("필요 품목", ["쌀", "생수", "상비약", "밀키트", "재난구호키트", "폭염대비세트", "신선식품"])
        amount = st.slider("요청 수량 (박스)", 1, 50, 10)
        
        if st.button("🚀 관제센터로 긴급 신청", use_container_width=True):
            with st.spinner('안전한 통신망으로 데이터를 전송 중입니다...'):
                time.sleep(1)
                loc = loc_dict[my_village]
                new = {"마을명": my_village, "품목": item, "수량": amount, "위도": loc[0], "경도": loc[1], "상태": "🚨위험" if amount > 30 else "✅정상", "배송": "대기중"}
                st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new])], ignore_index=True)
            st.toast(f'{my_village} 요청이 성공적으로 접수되었습니다!', icon='✅')

elif menu == "📊 통합 관제 보드":
    st.header("📊 통합 데이터 관제 보드")
    df = st.session_state['order_data']
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric(label="오늘 총 신청 건수", value=f"{len(df)}건", delta="2건 증가")
        col2.metric(label="누적 요청 수량", value=f"{df['수량'].sum()}개", delta="15% 증가", delta_color="inverse")
        col3.metric(label="🚨 위험 경보 발령", value=f"{len(df[df['상태'] == '🚨위험'])}건", delta="-1건 감소")
        
        st.divider()
        
        # [디벨롭] 3단 분할 레이아웃으로 차트와 데이터 동시 배치
        c1, c2, c3 = st.columns([1.2, 1.2, 1])
        with c1:
            st.subheader("💡 AI 주간 수요 예측 트렌드")
            # 시연용 가짜 시계열 데이터 생성
            chart_data = pd.DataFrame(
                np.random.randint(10, 50, size=(7, 2)),
                columns=['실제 수요(과거)', 'AI 예측(미래)'],
                index=pd.date_range(start="2026-06-27", periods=7)
            )
            st.line_chart(chart_data, color=["#4C78A8", "#FF9F9A"])
            
        with c2:
            st.subheader("📦 품목별 누적 수요")
            st.bar_chart(df.groupby("품목")["수량"].sum(), color="#4C78A8")
            
        with c3:
            st.subheader("📋 실시간 DB")
            st.dataframe(df[['마을명', '품목', '수량', '상태']], use_container_width=True, height=250)
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 데이터 추출(CSV)", csv_data, "data.csv", use_container_width=True)

elif menu == "🗺️ 3D 취약 지도":
    st.header("🗺️ 3D 실시간 취약지역 관제")
    df = st.session_state['order_data'].copy()
    
    if not df.empty:
        df['color'] = df['상태'].apply(lambda x: [255, 50, 50, 200] if x == "🚨위험" else [50, 150, 255, 200])
        
        layer = pdk.Layer(
            "ColumnLayer",
            df,
            get_position='[경도, 위도]',
            get_elevation='수량 * 100',
            elevation_scale=1,
            radius=1500,
            get_fill_color='color',
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(latitude=37.2, longitude=127.5, zoom=6.5, pitch=45)
        st.pydeck_chart(pdk.Deck(
            layers=[layer], initial_view_state=view_state,
            tooltip={"text": "{마을명}\n품목: {품목}\n요청수량: {수량}\n상태: {상태}"}
        ))

elif menu == "🚚 지능형 배송 매칭":
    st.header("🚚 지능형 긴급 배송 매칭")
    df = st.session_state['order_data']
    
    danger = df[(df['상태'] == "🚨위험") & (df['배송'] == "대기중")]
    completed = df[df['배송'] == "✅ 매칭완료"]
    
    # 상단: 처리해야 할 긴급 건
    if not danger.empty:
        st.error(f"⚠️ 현재 {len(danger)}건의 긴급 배송 대기 건이 있습니다.")
        for idx, row in danger.iterrows():
            with st.expander(f"🚨 {row['마을명']} 긴급 지원 요청 내역 (클릭)"):
                st.write(f"**필요 품목:** {row['품목']} / **요청 수량:** {row['수량']}박스")
                
                if st.button(f"물류창고 차량 매칭 승인", key=idx):
                    with st.spinner('인근 물류 창고와 통신하여 차량을 수배중입니다...'):
                        time.sleep(1.5)
                        st.session_state['order_data'].at[idx, '배송'] = "✅ 매칭완료"
                    st.toast(f"{row['마을명']} 배송 차량 배차가 완료되었습니다!", icon="🚛")
                    st.rerun()
    else:
        st.success("🎉 현재 처리 대기 중인 긴급 위험 안건이 없습니다.")
        
    st.divider()
    
    # [디벨롭] 하단: 처리 완료된 히스토리 표시
    st.subheader("🚛 금일 배차 완료 내역")
    if not completed.empty:
        st.dataframe(completed[['마을명', '품목', '수량', '배송']], use_container_width=True)
    else:
        st.info("아직 배차가 완료된 내역이 없습니다.")