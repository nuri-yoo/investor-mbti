"""
app.py
────────────────────────────────────────────────────────────
• 메인 애플리케이션 파일
• 페이지 라우팅 및 세션 상태 관리
"""

import streamlit as st
import pandas as pd
from questions import render as render_questions
from result_page import render as render_result
from sector_analysis import render as render_sector_analysis
from constants import QUESTIONNAIRE

def render_landing_page():
    """랜딩 페이지를 렌더링합니다."""
    st.title("📊 투자 MBTI 테스트")
    
    # 소개 텍스트
    st.markdown("""
    ### 나의 투자 성향은 무엇일까? 🤔
    
    간단한 테스트로 나만의 투자 스타일을 찾아보세요!
    
    ✨ 40개의 재미있는 질문으로 알아보는 투자 성향
    🧠 MBTI로 보는 나만의 투자 스타일
    💡 투자 성향에 맞는 섹터 추천
    📈 투자 성과 분석까지 한 번에!
    
    소요 시간: 약 5분
    """)
    
    # 시작 버튼
    if st.button("테스트 시작하기 ▶", use_container_width=True):
        st.session_state.current_page = "questions"
        st.rerun()
    
    # 법적 고지사항 (하단에 배치)
    st.markdown("---")
    st.caption("""
    ⚠️ 본 테스트는 투자 권유나 자문을 목적으로 하지 않습니다. 
    테스트 결과는 참고용으로만 활용하시기 바랍니다.
    """)
    
    # 문의 정보
    st.markdown("문의: nuriyoo@kaist.ac.kr")

def main():
    """메인 함수"""
    st.set_page_config(
        page_title="투자 MBTI 테스트",
        page_icon="📊",
        layout="wide"
    )
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "landing"
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'shuffled_questions' not in st.session_state:
        st.session_state.shuffled_questions = QUESTIONNAIRE.sample(frac=1).reset_index(drop=True)
    if 'mbti_type' not in st.session_state:
        st.session_state.mbti_type = None
    if 'recommended_sectors' not in st.session_state:
        st.session_state.recommended_sectors = []
    
    # 페이지 라우팅
    if st.session_state.current_page == "landing":
        render_landing_page()
    elif st.session_state.current_page == "questions":
        render_questions()
    elif st.session_state.current_page == "result":
        render_result()
    elif st.session_state.current_page == "sector_analysis":
        render_sector_analysis()

if __name__ == "__main__":
    main() 