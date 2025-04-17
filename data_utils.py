"""
data_utils.py
────────────────────────────────────────────────────────────
• 데이터 로딩 및 처리 유틸리티
• 섹터 데이터 분석 및 성과 지표 계산
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os
from datetime import datetime, timedelta

def calculate_max_drawdown(prices: pd.Series) -> float:
    """최대 낙폭(Maximum Drawdown)을 계산합니다.
    
    Args:
        prices (pd.Series): 가격 시계열 데이터
        
    Returns:
        float: 최대 낙폭 (음수 값)
    """
    # 누적 최대 가격
    rolling_max = prices.expanding().max()
    
    # 현재 가격과 누적 최대 가격의 차이를 계산
    drawdowns = (prices - rolling_max) / rolling_max
    
    # 최대 낙폭 반환
    return drawdowns.min()

def load_sector_data(sector_name: str, start_date=None, end_date=None) -> pd.DataFrame:
    """섹터 데이터를 로드하고 필터링합니다."""
    try:
        # 현재 파일의 디렉토리를 기준으로 data 디렉토리 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'data')
        
        # data 디렉토리가 없으면 생성
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # CSV 파일 경로
        file_path = os.path.join(data_dir, f"{sector_name}.csv")
        
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일이 존재하지 않습니다.")
            return None
            
        # CSV 파일 읽기 (UTF-8 인코딩 사용)
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 날짜와 종가 컬럼 처리
        df['Date'] = pd.to_datetime(df['날짜'])
        df['Close'] = df['지수'].astype(float)  # '종가' 대신 '지수' 컬럼 사용
        
        # 필요한 컬럼만 선택
        df = df[['Date', 'Close']]
        
        # 결측치 처리
        df = df.sort_values('Date')
        df = df.ffill()  # forward fill
        
        # 날짜 필터링
        if start_date and end_date:
            start = pd.Timestamp(start_date)
            end = pd.Timestamp(end_date)
            df = df[(df['Date'] >= start) & (df['Date'] <= end)]
            
        if df.empty:
            print(f"선택한 기간에 데이터가 없습니다: {sector_name}")
            return None
            
        return df
        
    except Exception as e:
        print(f"데이터 로딩 중 오류 발생 ({sector_name}): {str(e)}")
        return None

def calculate_performance_metrics(data: pd.DataFrame) -> Dict[str, float]:
    """성과 지표를 계산합니다."""
    try:
        if data is None or len(data) == 0:
            return {
                'total_return': 0.0,
                'annual_volatility': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'win_rate': 0.0
            }
        
        # 일간 수익률 계산
        daily_returns = data['Close'].pct_change().dropna()
        
        # 총 수익률
        total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
        
        # 연간 변동성
        annual_volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # 최대 낙폭
        max_drawdown = calculate_max_drawdown(data['Close']) * 100
        
        # 샤프 비율 (무위험 수익률 2% 가정)
        risk_free_rate = 0.02
        excess_returns = daily_returns - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / daily_returns.std()
        
        # 승률
        win_rate = (daily_returns > 0).sum() / len(daily_returns) * 100
        
        return {
            'total_return': round(total_return, 2),
            'annual_volatility': round(annual_volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate, 2)
        }
        
    except Exception as e:
        print(f"성과 지표 계산 중 오류 발생: {str(e)}")
        return None

def get_recommended_sectors(mbti_type: str) -> List[str]:
    """MBTI 유형에 따른 추천 섹터를 반환합니다."""
    from constants import MBTI_SECTORS
    
    if mbti_type in MBTI_SECTORS:
        return MBTI_SECTORS[mbti_type]
    return []
