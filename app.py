import streamlit as st
import pandas as pd
import pydeck as pdk
import time  # 로딩 애니메이션용

# 1. 페이지 설정 및 디자인(CSS) 튜닝
st.set_page_config(page_title="마을잇다 관제센터", page_icon="🚚", layout="wide")

# [깐지 포인트 1] 스트림릿 기본 메뉴와 워터마크를 숨겨서 진짜 앱처럼 보이게 만듭니다.
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. 세션 데이터 및 초기 목업(Mock) 데이터 설정
if 'order_data' not in st.session_state:
    # 빈 화면이 보이지 않도록 가상의 데이터를 미리 넣어둡니다. (시연용으로 최고입니다)
    initial_data = [
        {"마을명": "A마을", "품목": "생수", "수량": 45, "위도": 37.8, "경도": 128.8, "상태": "🚨위험", "배송": "대기중"},
        {"마을명": "B마을", "품목": "상비약", "수량": 15, "위도": 37.5, "경도": 126.8, "상태": "✅정상", "배송": "대기중"},
        {"마을명": "C마을", "품목": "기저귀", "수량": 35, "위도": 36.5, "경도": 127.5, "상태": "🚨위험", "배송": "대기중"}
    ]
    st.session_state['order_data'] = pd.DataFrame(initial_data)

admin_auth = {"admin_A": "A마을", "admin_B": "B마을", "admin_C": "C마을"}
loc_dict = {"A마을": [37.8, 128.8], "B마을": [37.5, 126.8], "C마을": [36.5, 127.5]}

# 3. 사이드바 및 로그인 UX 고도화
st.sidebar.title("🚚 마을잇다 플랫폼")
user_mode = st.sidebar.radio("접속 권한:", ("마을 관리자", "운영자(관제센터)"))
st.sidebar.divider()

menu = None
my_village = None

if user_mode == "마을 관리자":
    login_id = st.sidebar.text_input("🔑 관리자 ID (예: admin_A):")
    if login_id in admin_auth:
        my_village = admin_auth[login_id]
        menu = "수요 신청"
        st.sidebar.success(f"{my_village} 인증 완료") # 깔끔한 인증 알림
    elif login_id:
        st.sidebar.error("유효한 ID가 아닙니다.")
else:
    if st.sidebar.text_input("🔐 관제센터 비번 (1234):", type="password") == "1234":
        menu = st.sidebar.radio("관제 메뉴:", ("📊 통합 관제 보드", "🗺️ 3D 취약 지도", "🚚 지능형 배송 매칭"))
    elif st.sidebar.text_input:
        st.sidebar.warning("보안 인가가 필요합니다.")

# 4. 기능 로직 (깔쌈한 기능 추가)
if menu == "수요 신청":
    st.header(f"📦 {my_village} 전용 수요 신청")
    st.caption("마을에 긴급하게 필요한 물품을 관제센터로 요청합니다.")
    
    with st.container(border=True): # 입력 폼에 예쁜 테두리 추가
        item = st.selectbox("필요 품목", ["쌀", "생수", "상비약", "밀키트", "기저귀", "신선식품"])
        amount = st.slider("요청 수량 (박스)", 1, 50, 10)
        
        if st.button("🚀 관제센터로 신청 전송", use_container_width=True): # 꽉 차는 버튼
            # [깐지 포인트 2] 스피너를 돌려 진짜 서버에 전송하는 듯한 연출
            with st.spinner('안전한 통신망으로 데이터를 전송 중입니다...'):
                time.sleep(1) # 1초 대기 (연출용)
                loc = loc_dict[my_village]
                new = {"마을명": my_village, "품목": item, "수량": amount, "위도": loc[0], "경도": loc[1], "상태": "🚨위험" if amount > 30 else "✅정상", "배송": "대기중"}
                st.session_state['order_data'] = pd.concat([st.session_state['order_data'], pd.DataFrame([new])], ignore_index=True)
            
            # [깐지 포인트 3] 화면 상단 알림 대신 우측 하단 토스트(Toast) 팝업 사용
            st.toast(f'{my_village} 요청이 성공적으로 접수되었습니다!', icon='✅')

elif menu == "📊 통합 관제 보드":
    st.header("📊 통합 데이터 관제 보드")
    df = st.session_state['order_data']
    
    if not df.empty:
        # [깐지 포인트 4] 어제 대비 증감(Delta)을 보여주는 지표 (값은 시연용 하드코딩)
        col1, col2, col3 = st.columns(3)
        col1.metric(label="오늘 총 신청 건수", value=f"{len(df)}건", delta="2건 증가")
        col2.metric(label="누적 요청 수량", value=f"{df['수량'].sum()}개", delta="15% 증가", delta_color="inverse")
        col3.metric(label="🚨 위험 경보 발령 마을", value=f"{len(df[df['상태'] == '🚨위험'])}곳", delta="-1곳 감소")
        
        st.divider()
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("품목별 수요 동향")
            st.bar_chart(df.groupby("품목")["수량"].sum(), color="#4C78A8")
        with c2:
            st.subheader("실시간 데이터베이스")
            st.dataframe(df[['마을명', '품목', '수량', '상태']], use_container_width=True)
            st.download_button("📥 백업용 CSV 다운로드", df.to_csv(index=False), "data.csv", use_container_width=True)

elif menu == "🗺️ 3D 취약 지도":
    st.header("🗺️ 3D 실시간 취약지역 관제")
    df = st.session_state['order_data']
    if not df.empty:
        # [깐지 포인트 5] 지도의 높이(elevation)를 수량에 비례하게 설정하여 3D 효과 극대화
        layer = pdk.Layer(
            "ColumnLayer",
            df,
            get_position='[경도, 위도]',
            get_elevation='수량 * 100', # 수량이 많을수록 기둥이 높아짐
            elevation_scale=1,
            radius=1500,
            get_fill_color='[255, 50, 50, 200] if 상태 == "🚨위험" else [50, 150, 255, 200]',
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(latitude=37.2, longitude=127.5, zoom=6.5, pitch=45) # pitch로 기울기 줘서 3D 강조
        st.pydeck_chart(pdk.Deck(
            layers=[layer], initial_view_state=view_state,
            tooltip={"text": "{마을명}\n품목: {품목}\n요청수량: {수량}\n상태: {상태}"}
        ))

elif menu == "🚚 지능형 배송 매칭":
    st.header("🚚 지능형 긴급 배송 매칭")
    df = st.session_state['order_data']
    
    # '대기중'이면서 '위험'인 건만 필터링
    danger = df[(df['상태'] == "🚨위험") & (df['배송'] == "대기중")]
    
    if not danger.empty:
        st.error(f"⚠️ 현재 {len(danger)}건의 긴급 배송 대기 건이 있습니다.")
        for idx, row in danger.iterrows():
            with st.expander(f"🚨 {row['마을명']} 긴급 지원 요청 내역 (클릭하여 매칭)"):
                st.write(f"**필요 품목:** {row['품목']} / **수량:** {row['수량']}박스")
                
                if st.button(f"물류창고 차량 매칭 승인", key=idx):
                    with st.spinner('인근 물류 창고와 통신하여 차량을 수배중입니다...'):
                        time.sleep(1.5)
                        st.session_state['order_data'].at[idx, '배송'] = "✅ 매칭완료"
                    st.toast(f"{row['마을명']} 배송 차량 배차가 완료되었습니다!", icon="🚛")
                    st.rerun() # 화면 새로고침하여 리스트에서 없애기
    else:
        st.success("🎉 현재 처리 대기 중인 긴급 위험 안건이 없습니다. (모두 매칭 완료)")