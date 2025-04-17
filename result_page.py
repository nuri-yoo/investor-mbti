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
from constants import MBTI_DESCRIPTIONS, MBTI_SECTORS, SECTOR_MATRIX, QUESTIONNAIRE

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
        # 질문 정보 가져오기
        question = QUESTIONNAIRE[QUESTIONNAIRE['qid'] == qid].iloc[0]
        axis = question['axis']
        side = question['side']
        
        # 답변이 1(그렇다)이면 해당 side에 점수 추가
        if answer == 1:
            scores[side] += 1
        # 답변이 0(아니다)이면 반대 side에 점수 추가
        else:
            opposite = {'I': 'E', 'E': 'I', 
                       'N': 'S', 'S': 'N',
                       'T': 'F', 'F': 'T',
                       'J': 'P', 'P': 'J'}[side]
            scores[opposite] += 1
    
    # 각 축별로 더 높은 점수를 가진 유형 선택
    mbti = ''
    mbti += 'I' if scores['I'] > scores['E'] else 'E'  # 동점일 경우 E 선택
    mbti += 'N' if scores['N'] > scores['S'] else 'S'  # 동점일 경우 S 선택
    mbti += 'T' if scores['T'] > scores['F'] else 'F'  # 동점일 경우 F 선택
    mbti += 'J' if scores['J'] > scores['P'] else 'P'  # 동점일 경우 P 선택
    
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

def create_monthly_heatmap(monthly_returns):
    """월별 수익률 히트맵을 생성합니다."""
    # 월별 수익률을 2차원 배열로 변환
    monthly_matrix = monthly_returns.values.reshape(-1, 12)
    
    # 히트맵 생성
    fig = go.Figure(data=go.Heatmap(
        z=monthly_matrix,
        x=['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
        colorscale='RdYlGn',
        zmid=0,
        showscale=True
    ))
    
    fig.update_layout(
        title='월별 수익률 히트맵',
        xaxis_title='월',
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            showline=False,
            zeroline=False
        ),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_price_chart(data):
    """지수 추이 차트를 생성합니다."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        mode='lines',
        name='지수 추이',
        line=dict(color='#1f77b4')
    ))
    
    fig.update_layout(
        title='지수 추이',
        xaxis_title='날짜',
        yaxis_title='지수',
        hovermode='x unified',
        height=400
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

def render_sector_analysis():
    """섹터 분석 결과를 표시합니다."""
    st.title("📊 섹터 분석")
    
    # 날짜 범위 선택
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "시작일",
            value=st.session_state.start_date,
            min_value=datetime(2010, 1, 1),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "종료일",
            value=st.session_state.end_date,
            min_value=datetime(2010, 1, 1),
            max_value=datetime.now()
        )
    
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    
    # 추천 섹터 데이터 로드 및 분석
    if st.session_state.recommended_sectors:
        for sector in st.session_state.recommended_sectors:
            st.markdown(f"### {sector} 섹터 분석")
            
            try:
                # 섹터 데이터 로드
                data = load_sector_data(sector, start_date, end_date)
                
                # 성과 지표 계산
                metrics = calculate_performance_metrics(data)
                
                # 지수 추이 차트 표시
                st.plotly_chart(create_price_chart(data))
                
                # 성과 지표 표시
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("수익률", f"{metrics['return']:.1f}%")
                with col2:
                    st.metric("최대 낙폭", f"{metrics['max_drawdown']:.1f}%")
                with col3:
                    st.metric("변동성", f"{metrics['volatility']:.1f}%")
                with col4:
                    st.metric("샤프 비율", f"{metrics['sharpe_ratio']:.2f}")
                
                # 월별 수익률 히트맵 표시
                monthly_returns = data.set_index('Date')['Close'].pct_change().resample('M').apply(lambda x: (1 + x).prod() - 1)
                st.plotly_chart(create_monthly_heatmap(monthly_returns))
                
            except Exception as e:
                st.error(f"{sector} 섹터 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
    
    # 이전 페이지로 돌아가기
    if st.button("◀ MBTI 결과로 돌아가기"):
        st.session_state.current_page = "result"
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
