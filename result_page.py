"""
result_page.py
────────────────────────────────────────────────────────────
• MBTI 결과 페이지
• MBTI 유형 계산 및 결과 표시
• 추천 섹터 표시
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_utils import load_sector_data, calculate_performance_metrics
from datetime import datetime
from constants import MBTI_DESCRIPTIONS, MBTI_SECTORS, SECTOR_MATRIX

def calculate_mbti_type(answers: dict) -> str:
    """MBTI 유형을 계산합니다."""
    scores = {
        'I': 0, 'E': 0,
        'N': 0, 'S': 0,
        'T': 0, 'F': 0,
        'J': 0, 'P': 0
    }
    
    # 각 답변에 대해 해당하는 점수를 증가
    for qid, answer in answers.items():
        if answer in scores:
            scores[answer] += 1
    
    # 각 축별로 더 높은 점수를 가진 유형 선택
    mbti = ''
    mbti += 'I' if scores['I'] >= scores['E'] else 'E'
    mbti += 'N' if scores['N'] >= scores['S'] else 'S'
    mbti += 'T' if scores['T'] >= scores['F'] else 'F'
    mbti += 'J' if scores['J'] >= scores['P'] else 'P'
    
    return mbti

def create_radar_chart(mbti_type: str):
    """MBTI 유형의 특성을 레이더 차트로 표시합니다."""
    if mbti_type not in MBTI_SECTORS:
        return None
        
    recommended_sectors = MBTI_SECTORS[mbti_type]
    sector_scores = []
    
    for sector in recommended_sectors:
        if sector in SECTOR_MATRIX:
            sector_scores.append(SECTOR_MATRIX[sector])
    
    if not sector_scores:
        return None
        
    # 평균 점수 계산
    avg_scores = np.mean(sector_scores, axis=0)
    
    # 레이더 차트 카테고리
    categories = [
        '안정성', '변동성',
        '성장성', '가치성',
        '기술성', '전통성',
        '보수성', '공격성'
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=avg_scores,
        theta=categories,
        fill='toself',
        name=mbti_type
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True
    )
    
    return fig

def render_mbti_result(mbti_type: str):
    """MBTI 결과를 표시합니다."""
    st.markdown(f"## 당신의 투자 MBTI는 **{mbti_type}** 입니다!")
    
    # MBTI 설명 표시
    if mbti_type in MBTI_DESCRIPTIONS:
        desc = MBTI_DESCRIPTIONS[mbti_type]
        st.markdown(f"### {desc['description']}")
        
        # 강점과 약점
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💪 투자 강점")
            for strength in desc['strengths']:
                st.markdown(f"- {strength}")
        
        with col2:
            st.markdown("#### 🚨 투자 약점")
            for weakness in desc['weaknesses']:
                st.markdown(f"- {weakness}")
    
    # 레이더 차트
    st.markdown("### 📊 투자 성향 분석")
    fig = create_radar_chart(mbti_type)
    if fig:
        st.plotly_chart(fig)
    
    # 추천 섹터
    if mbti_type in MBTI_SECTORS:
        st.markdown("### 🎯 추천 투자 섹터")
        recommended_sectors = MBTI_SECTORS[mbti_type]
        st.session_state.recommended_sectors = recommended_sectors
        
        for sector in recommended_sectors:
            st.markdown(f"- **{sector}**")
        
        # 섹터 분석 페이지로 이동
        if st.button("📈 섹터 분석 보기"):
            st.session_state.current_page = "sector_analysis"
            st.rerun()

def render():
    """결과 페이지를 렌더링합니다."""
    st.title("🎯 투자 성향 분석 결과")
    
    # 이전 페이지로 돌아가기
    if st.button("◀ 테스트 다시하기"):
        st.session_state.current_page = "landing"
        st.session_state.answers = {}
        st.session_state.current_question = 0
        st.rerun()
    
    mbti_type = calculate_mbti_type(st.session_state.answers)
    st.session_state.mbti_type = mbti_type
    render_mbti_result(mbti_type)
