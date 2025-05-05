import pandas as pd
import numpy as np

def calculate_returns(data):
    """
    株価データからリターンを計算する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
        
    Returns:
    --------
    pandas.DataFrame
        リターンを追加したデータフレーム
    """
    df = data.copy()
    df['Daily_Return'] = df['Close'].pct_change() * 100
    df['Cumulative_Return'] = (1 + df['Daily_Return'] / 100).cumprod() - 1
    df['Cumulative_Return'] = df['Cumulative_Return'] * 100
    return df

def calculate_moving_averages(data, windows=[5, 20, 60, 120]):
    """
    移動平均を計算する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    windows : list, optional
        移動平均の期間リスト
        
    Returns:
    --------
    pandas.DataFrame
        移動平均を追加したデータフレーム
    """
    df = data.copy()
    for window in windows:
        df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

def calculate_volatility(data, window=20):
    """
    ボラティリティを計算する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    window : int, optional
        ボラティリティの計算期間
        
    Returns:
    --------
    pandas.DataFrame
        ボラティリティを追加したデータフレーム
    """
    df = data.copy()
    df['Volatility'] = df['Daily_Return'].rolling(window=window).std()
    return df

def calculate_rsi(data, window=14):
    """
    RSI (Relative Strength Index)を計算する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    window : int, optional
        RSIの計算期間
        
    Returns:
    --------
    pandas.DataFrame
        RSIを追加したデータフレーム
    """
    df = data.copy()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df
