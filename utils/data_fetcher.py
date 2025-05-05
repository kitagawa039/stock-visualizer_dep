import os
import requests
import pandas as pd
from utils.jquants_api import get_stock_data

def get_stock_data_alpha_vantage(symbol, outputsize="full"):
    """
    Alpha Vantage APIから株価データを取得する関数
    
    Parameters:
    -----------
    symbol : str
        ティッカーシンボル（例: "AAPL", "MSFT"）
    outputsize : str, optional
        取得するデータ量（"compact"または"full"）
        
    Returns:
    --------
    pandas.DataFrame
        株価データ
    """
    try:
        api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "demo")
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_DAILY"
            f"&symbol={symbol}"
            f"&outputsize={outputsize}"
            f"&apikey={api_key}"
        )
        r = requests.get(url)
        data = r.json()
        
        if "Time Series (Daily)" not in data:
            error_msg = data.get("Note") or data.get("Error Message") or str(data)
            raise ValueError("データ取得失敗: " + error_msg)
            
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adj Close",
            "6. volume": "Volume"
        })
        
        columns_to_keep = ["Open", "High", "Low", "Close", "Volume", "Adj Close"]
        available_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[available_columns]
        
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    except Exception as e:
        raise ValueError(f"Alpha Vantage APIデータ取得エラー: {e}")


def get_stock_data_jquants(symbol, from_date=None, to_date=None):
    """
    J-Quants APIから株価データを取得する関数
    jquants_apiモジュールを使用
    
    Parameters:
    -----------
    symbol : str
        証券コード（例: "1321.T"）
    from_date : str, optional
        取得開始日（YYYY-MM-DD形式）
    to_date : str, optional
        取得終了日（YYYY-MM-DD形式）
        
    Returns:
    --------
    pandas.DataFrame
        株価データ
    """
    return get_stock_data(symbol, from_date, to_date)
