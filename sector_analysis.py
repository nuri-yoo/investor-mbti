"""
sector_analysis.py
────────────────────────────────────────────────────────────
• 섹터별 성과 분석 페이지
• 추천 섹터의 성과 지표 및 시각화
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px
from data_utils import load_sector_data, calculate_performance_metrics, calculate_max_drawdown
from datetime import datetime, date, timedelta
from constants import SECTOR_CODES

# 섹터 파일명 매핑 (실제 파일명과 정확히 일치)
SECTOR_FILE_NAMES = {
    "일반서비스": "일반서비스",
    "보험": "보험",
    "증권": "증권",
    "금융": "금융",
    "통신": "통신",
    "운송·창고": "운송·창고",
    "건설": "건설",
    "전기·가스": "전기·가스",
    "유통": "유통",
    "운송장비·부품": "운송장비·부품",
    "의료·정밀기기": "의료·정밀기기",
    "전기전자": "전기전자",
    "기계·장비": "기계·장비",
    "금속": "금속",
    "비금속": "비금속",
    "제약": "제약",
    "화학": "화학",
    "종이·목재": "종이·목재",
    "섬유·의류": "섬유·의류"
}

def render():
    """섹터 분석 페이지를 렌더링합니다."""
    st.title("📈 섹터 성과 분석")
    
    # 이전 페이지로 돌아가기
    if st.button("◀ MBTI 결과로 돌아가기"):
        st.session_state.current_page = "result"
        st.rerun()
    
    # 추천 섹터 확인
    if 'recommended_sectors' not in st.session_state or not st.session_state.recommended_sectors:
        st.error("추천 섹터가 없습니다. MBTI 테스트를 다시 진행해주세요.")
        return
    
    # 분석 기간 설정
    st.subheader("📅 분석 기간 설정")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "시작일",
            value=datetime(2024, 1, 1).date(),
            min_value=datetime(2020, 1, 1).date(),
            max_value=datetime.now().date()
        )
    with col2:
        end_date = st.date_input(
            "종료일",
            value=datetime(2024, 12, 31).date(),
            min_value=start_date,
            max_value=datetime.now().date()
        )
    
    # 섹터 데이터 로드 및 분석
    st.subheader("📊 섹터별 성과 분석")
    
    # 섹터별 데이터 저장
    sector_data = {}
    
    # 섹터별 성과 지표 계산
    for sector in st.session_state.recommended_sectors:
        st.markdown(f"### {sector}")
        
        # 파일명 생성
        file_name = SECTOR_FILE_NAMES.get(sector, sector)
        
        # 데이터 로드
        df = load_sector_data(file_name, start_date, end_date)
        if df is None or df.empty:
            st.warning(f"{sector} 데이터를 로드할 수 없습니다.")
            continue
        
        try:
            # 수익률 계산
            df['Daily_Return'] = df['Close'].pct_change()
            
            # 성과 지표 계산
            total_return = ((1 + df['Daily_Return']).prod() - 1) * 100
            annual_vol = df['Daily_Return'].std() * np.sqrt(252) * 100
            max_drawdown = calculate_max_drawdown(df['Close']) * 100
            win_rate = (df['Daily_Return'] > 0).mean() * 100
            
            # 성과 지표 표시
            metrics_col1, metrics_col2 = st.columns(2)
            with metrics_col1:
                st.metric("총 수익률", f"{total_return:.1f}%")
                st.metric("연간 변동성", f"{annual_vol:.1f}%")
            with metrics_col2:
                st.metric("최대 낙폭", f"{max_drawdown:.1f}%")
                st.metric("승률", f"{win_rate:.1f}%")
            
            # 지수 추이 차트
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Close'],
                mode='lines',
                name='종가'
            ))
            fig.update_layout(
                title=f"{sector} 지수 추이",
                xaxis_title="날짜",
                yaxis_title="지수",
                showlegend=True
            )
            st.plotly_chart(fig)
            
            # 월별 수익률 히트맵
            df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
            monthly_returns = df.groupby('YearMonth')['Daily_Return'].sum() * 100
            
            fig = go.Figure(data=go.Heatmap(
                z=[monthly_returns.values],
                x=monthly_returns.index,
                colorscale='RdYlGn',
                text=[[f"{x:.1f}%" for x in monthly_returns.values]],
                texttemplate="%{text}",
                textfont={"size": 10},
                showscale=True
            ))
            fig.update_layout(
                title=f"{sector} 월별 수익률 히트맵",
                height=200
            )
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"{sector} 섹터 분석 중 오류가 발생했습니다: {str(e)}")
            continue
            
        st.markdown("---")

def calculate_max_drawdown(prices):
    """최대 낙폭을 계산합니다."""
    cumulative_returns = (1 + prices.pct_change()).cumprod()
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = (cumulative_returns - rolling_max) / rolling_max
    return drawdowns.min() 