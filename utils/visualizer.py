import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import requests

def plot_candlestick(data, title="日経225株価チャート"):
    """
    ローソク足チャートを作成する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    title : str, optional
        チャートのタイトル
        
    Returns:
    --------
    plotly.graph_objects.Figure
        ローソク足チャート
    """
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="OHLC"
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title="日付",
        yaxis_title="価格",
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_line_chart(data, columns=['Close'], title="日経225株価推移"):
    """
    折れ線グラフを作成する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    columns : list, optional
        プロットする列名のリスト
    title : str, optional
        チャートのタイトル
        
    Returns:
    --------
    plotly.graph_objects.Figure
        折れ線グラフ
    """
    fig = go.Figure()
    
    for column in columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[column],
            mode='lines',
            name=column
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="日付",
        yaxis_title="価格",
        legend_title="指標"
    )
    
    return fig

def plot_volume(data, title="取引量"):
    """
    出来高チャートを作成する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    title : str, optional
        チャートのタイトル
        
    Returns:
    --------
    plotly.graph_objects.Figure
        出来高チャート
    """
    fig = go.Figure(data=[go.Bar(
        x=data.index,
        y=data['Volume'],
        name="Volume"
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title="日付",
        yaxis_title="出来高"
    )
    
    return fig

def plot_returns_histogram(data, title="日次リターン分布"):
    """
    リターンのヒストグラムを作成する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        リターンを含む株価データ
    title : str, optional
        チャートのタイトル
        
    Returns:
    --------
    plotly.graph_objects.Figure
        ヒストグラム
    """
    fig = px.histogram(
        data, 
        x="Daily_Return",
        nbins=50,
        title=title
    )
    
    fig.update_layout(
        xaxis_title="日次リターン (%)",
        yaxis_title="頻度"
    )
    
    return fig

def plot_correlation_heatmap(data, columns=None, title="相関ヒートマップ"):
    """
    相関ヒートマップを作成する関数
    
    Parameters:
    -----------
    data : pandas.DataFrame
        株価データ
    columns : list, optional
        相関を計算する列名のリスト
    title : str, optional
        チャートのタイトル
        
    Returns:
    --------
    plotly.graph_objects.Figure
        相関ヒートマップ
    """
    if columns is None:
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    corr_matrix = data[columns].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title=title
    )
    
    return fig

def get_stock_data_alpha_vantage(symbol, outputsize="full"):
    api_key = os.environ["ALPHAVANTAGE_API_KEY"]
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={symbol}"
        f"&outputsize={outputsize}"
        f"&apikey={api_key}"
    )
    r = requests.get(url)
    data = r.json()
    # エラー詳細を表示
    if "Time Series (Daily)" not in data:
        error_msg = data.get("Note") or data.get("Error Message") or str(data)
        raise ValueError("データ取得失敗: " + error_msg)
    # ...（以下略）
