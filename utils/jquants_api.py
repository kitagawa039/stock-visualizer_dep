"""
J-Quants API関連の機能を提供するユーティリティモジュール
"""
import os
import requests
import json
import pandas as pd
from datetime import datetime, date

# J-Quants APIのサブスクリプション対象期間
SUBSCRIPTION_START_DATE = "2023-02-10"
SUBSCRIPTION_END_DATE = "2025-02-10"

def get_refresh_token():
    """
    J-Quants APIからリフレッシュトークンを取得する関数
    
    Returns:
    --------
    str
        リフレッシュトークン
        
    Raises:
    -------
    ValueError
        トークン取得に失敗した場合
    """
    try:
        email = os.environ.get("JQUANTS_EMAIL")
        password = os.environ.get("JQUANTS_PASSWORD")
        
        if not email or not password:
            raise ValueError("環境変数 JQUANTS_EMAIL または JQUANTS_PASSWORD が設定されていません")
            
        url = "https://api.jquants.com/v1/token/auth_user"
        res = requests.post(url, json={"mailaddress": email, "password": password})
        res.raise_for_status()  # HTTPエラーがあれば例外を発生
        
        response_json = res.json()
        
        refresh_token = response_json.get("refreshToken")
        
        if refresh_token:
            return refresh_token
        else:
            raise ValueError(f"リフレッシュトークン取得失敗: refreshTokenがレスポンスに含まれていません。レスポンス: {response_json}")
                
    except requests.exceptions.RequestException as e:
        raise ValueError(f"J-Quants APIリクエストエラー: {e}")
    except json.JSONDecodeError:
        raise ValueError(f"J-Quants API JSONデコードエラー: {res.text}")
    except Exception as e:
        raise ValueError(f"J-Quants APIリフレッシュトークン取得エラー: {e}")

def get_id_token(refresh_token):
    """
    J-Quants APIからIDトークンを取得する関数
    
    Parameters:
    -----------
    refresh_token : str
        リフレッシュトークン
        
    Returns:
    --------
    str
        IDトークン
        
    Raises:
    -------
    ValueError
        IDトークン取得に失敗した場合
    """
    try:
        id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
        params = {"refreshtoken": refresh_token}
        
        id_token_res = requests.post(id_token_url, params=params)
        id_token_res.raise_for_status()
        
        id_token_json = id_token_res.json()
        id_token = id_token_json.get("idToken")
        
        if not id_token:
            raise ValueError(f"IDトークン取得失敗: idTokenがレスポンスに含まれていません。レスポンス: {id_token_json}")
        
        return id_token
    except requests.exceptions.RequestException as e:
        raise ValueError(f"J-Quants API IDトークンリクエストエラー: {e}")
    except json.JSONDecodeError:
        raise ValueError(f"J-Quants API IDトークン JSONデコードエラー: {id_token_res.text}")
    except Exception as e:
        raise ValueError(f"J-Quants API IDトークン取得エラー: {e}")

def get_jquants_token():
    """
    J-Quants APIからトークンを取得する関数（互換性のため残す）
    
    Returns:
    --------
    str
        IDトークン
        
    Raises:
    -------
    ValueError
        トークン取得に失敗した場合
    """
    refresh_token = get_refresh_token()
    return get_id_token(refresh_token)

def validate_date_range(from_date, to_date):
    """
    日付範囲がサブスクリプション対象期間内かどうかを検証する関数
    
    Parameters:
    -----------
    from_date : str
        取得開始日（YYYY-MM-DD形式）
    to_date : str
        取得終了日（YYYY-MM-DD形式）
        
    Returns:
    --------
    tuple
        (有効な開始日, 有効な終了日)
        
    Raises:
    -------
    ValueError
        日付範囲が完全にサブスクリプション対象期間外の場合
    """
    subscription_start = datetime.strptime(SUBSCRIPTION_START_DATE, "%Y-%m-%d").date()
    subscription_end = datetime.strptime(SUBSCRIPTION_END_DATE, "%Y-%m-%d").date()
    
    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else subscription_start
    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else date.today()
    
    if from_date_obj > subscription_end or to_date_obj < subscription_start:
        raise ValueError(
            f"指定された日付範囲 ({from_date} ~ {to_date}) はサブスクリプション対象期間 "
            f"({SUBSCRIPTION_START_DATE} ~ {SUBSCRIPTION_END_DATE}) 外です。"
        )
    
    valid_from = max(from_date_obj, subscription_start)
    valid_to = min(to_date_obj, subscription_end)
    
    return valid_from.strftime("%Y-%m-%d"), valid_to.strftime("%Y-%m-%d")

def get_stock_data(symbol, from_date=None, to_date=None):
    """
    J-Quants APIから株価データを取得する関数
    
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
        
    Raises:
    -------
    ValueError
        データ取得に失敗した場合
    """
    try:
        code = symbol.replace('.T', '')
        
        if from_date:
            try:
                datetime.strptime(from_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"from_dateの形式が不正です: {from_date}。YYYY-MM-DD形式である必要があります。")
        
        if to_date:
            try:
                datetime.strptime(to_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"to_dateの形式が不正です: {to_date}。YYYY-MM-DD形式である必要があります。")
        
        if from_date or to_date:
            valid_from, valid_to = validate_date_range(
                from_date or SUBSCRIPTION_START_DATE, 
                to_date or date.today().strftime("%Y-%m-%d")
            )
        else:
            valid_from = "2023-03-01"
            valid_to = "2023-03-31"
        
        # リフレッシュトークンを取得
        refresh_token = get_refresh_token()
        
        id_token = get_id_token(refresh_token)
        
        url = "https://api.jquants.com/v1/prices/daily_quotes"
        headers = {"Authorization": f"Bearer {id_token}"}
        
        params = {
            "code": code,
            "from": valid_from,
            "to": valid_to
        }
            
        res = requests.get(url, headers=headers, params=params)
        
        if res.status_code != 200:
            error_msg = f"J-Quants APIエラー: ステータスコード {res.status_code}"
            try:
                error_json = res.json()
                if "message" in error_json:
                    error_msg += f", メッセージ: {error_json['message']}"
            except:
                error_msg += f", レスポンス: {res.text}"
            raise ValueError(error_msg)
        
        data_json = res.json()
        data = data_json.get("daily_quotes", [])
        
        if not data:
            raise ValueError(f"J-Quants APIデータ取得失敗: データが空です。レスポンス: {data_json}")
                
        df = pd.DataFrame(data)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        
        columns_to_extract = ["Open", "High", "Low", "Close", "Volume"]
        available_columns = [col for col in columns_to_extract if col in df.columns]
        
        if not available_columns:
            raise ValueError(f"J-Quants APIデータ取得失敗: 必要なカラムがありません。利用可能なカラム: {list(df.columns)}")
        
        df = df[available_columns].astype(float)
        return df
            
    except ValueError:
        # ValueErrorはそのまま再発生させる
        raise
    except Exception as e:
        raise ValueError(f"J-Quants APIデータ取得エラー: {e}")
