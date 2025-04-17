"""
questions.py
────────────────────────────────────────────────────────────
• MBTI 질문 페이지
• 40개의 재미있는 투자 성향 질문
"""

import streamlit as st
import pandas as pd
import numpy as np
from constants import QUESTIONNAIRE

def get_shuffled_questions():
    """질문을 랜덤하게 섞어서 반환합니다."""
    questions = QUESTIONNAIRE.copy()
    questions = questions.sample(frac=1).reset_index(drop=True)
    return questions

def render():
    """질문 페이지를 렌더링합니다."""
    st.title("📊 투자 MBTI 테스트")
    st.markdown("#### 간단한 질문으로 나만의 투자 스타일을 찾아보세요! 😊")
    
    # 세션 상태 초기화
    if 'shuffled_questions' not in st.session_state:
        st.session_state.shuffled_questions = get_shuffled_questions()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    # 진행 상황 표시
    current = st.session_state.current_question
    total_questions = len(st.session_state.shuffled_questions)
    
    # 마지막 질문을 넘어간 경우 결과 페이지로 이동
    if current >= total_questions:
        st.session_state.current_page = "result"
        st.rerun()
        return
    
    progress = min(current / total_questions, 1.0)
    st.progress(progress)
    st.markdown(f"**{current + 1} / {total_questions}**")
    
    try:
        # 현재 질문 표시
        question = st.session_state.shuffled_questions.iloc[current]
        st.markdown(f"### {question['text']}")
        
        # 답변 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("그렇다", use_container_width=True):
                st.session_state.answers[question['qid']] = 1
                st.session_state.current_question += 1
                st.rerun()
        with col2:
            if st.button("아니다", use_container_width=True):
                st.session_state.answers[question['qid']] = 0
                st.session_state.current_question += 1
                st.rerun()
    except IndexError:
        # 인덱스 오류 발생 시 결과 페이지로 이동
        st.session_state.current_page = "result"
        st.rerun()
        return
    
    # 문의 정보
    st.markdown("---")
    st.markdown("문의: nuriyoo@kaist.ac.kr") 