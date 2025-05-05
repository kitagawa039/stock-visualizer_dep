import os
import requests
import pandas as pd
import json
from datetime import datetime, timedelta

def get_jquants_token():
    """
    J-Quants APIからトークンを取得する関数
    より堅牢なエラーハンドリングを実装
    """
    try:
        email = os.environ.get("JQUANTS_EMAIL")
        password = os.environ.get("JQUANTS_PASSWORD")
        
        if not email or not password:
            print("環境変数 JQUANTS_EMAIL または JQUANTS_PASSWORD が設定されていません")
            return None
            
        url = "https://api.jquants.com/v1/token/auth_user"
        res = requests.post(url, json={"mailaddress": email, "password": password})
        
        print(f"ステータスコード: {res.status_code}")
        print(f"レスポンスヘッダー: {res.headers}")
        
        try:
            response_json = res.json()
            print(f"レスポンス本文: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            
            id_token = response_json.get("idToken")
            if id_token:
                print("トークン取得成功!")
                return id_token
            else:
                print(f"トークン取得失敗: idTokenがレスポンスに含まれていません")
                return None
                
        except json.JSONDecodeError:
            print(f"JSONデコードエラー: {res.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        return None

def get_stock_data_jquants(symbol, from_date=None, to_date=None):
    """
    J-Quants APIから株価データを取得する関数
    より堅牢なエラーハンドリングを実装
    """
    try:
        id_token = get_jquants_token()
        if not id_token:
            print("トークンが取得できなかったため、株価データを取得できません")
            return None
            
        refresh_url = "https://api.jquants.com/v1/token/refresh"
        refresh_headers = {"Authorization": f"Bearer {id_token}"}
        refresh_res = requests.post(refresh_url, headers=refresh_headers)
        
        print(f"リフレッシュトークンステータスコード: {refresh_res.status_code}")
        
        try:
            refresh_json = refresh_res.json()
            print(f"リフレッシュトークンレスポンス: {json.dumps(refresh_json, indent=2, ensure_ascii=False)}")
            
            refresh_token = refresh_json.get("idToken")
            if not refresh_token:
                print("リフレッシュトークン取得失敗")
                return None
                
            token_to_use = refresh_token
                
        except json.JSONDecodeError:
            print(f"リフレッシュトークンJSONデコードエラー: {refresh_res.text}")
            token_to_use = id_token
        
        url = "https://api.jquants.com/v1/prices/daily_quotes"
        headers = {"Authorization": f"Bearer {token_to_use}"}
        
        code = symbol.replace('.T', '')
        
        params = {"code": code}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
            
        print(f"リクエストパラメータ: {params}")
        
        res = requests.get(url, headers=headers, params=params)
        print(f"株価データステータスコード: {res.status_code}")
        
        try:
            data_json = res.json()
            print(f"株価データレスポンスキー: {list(data_json.keys())}")
            
            data = data_json.get("daily_quotes", [])
            if not data:
                print(f"株価データ取得失敗: データが空です。レスポンス: {json.dumps(data_json, indent=2, ensure_ascii=False)}")
                return None
                
            print(f"取得したデータ件数: {len(data)}")
            if len(data) > 0:
                print(f"最初のデータ: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
                
            df = pd.DataFrame(data)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
            
            df = df.rename(columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume"
            })
            
            df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
            return df
            
        except json.JSONDecodeError:
            print(f"株価データJSONデコードエラー: {res.text}")
            return None
        except Exception as e:
            print(f"データ処理エラー: {e}")
            return None
            
    except Exception as e:
        print(f"予期せぬエラー: {e}")
        return None

def test_token_retrieval():
    """トークン取得のテスト"""
    print("=== トークン取得テスト ===")
    token = get_jquants_token()
    if token:
        print(f"トークン: {token[:10]}...（セキュリティのため一部のみ表示）")
        return True
    else:
        print("トークン取得に失敗しました")
        return False

def test_data_retrieval():
    """データ取得のテスト"""
    print("\n=== データ取得テスト ===")
    symbol = "1321.T"
    today = datetime.now().date()
    from_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    print(f"銘柄: {symbol}")
    print(f"期間: {from_date} から {to_date}")
    
    data = get_stock_data_jquants(symbol, from_date=from_date, to_date=to_date)
    if data is not None and not data.empty:
        print(f"データ取得成功！行数: {len(data)}")
        print("\nデータサンプル:")
        print(data.head())
        return True
    else:
        print("データ取得に失敗しました")
        return False

if __name__ == "__main__":
    print("J-Quants API テストスクリプト")
    print("----------------------------")
    
    email = os.environ.get("JQUANTS_EMAIL")
    password = os.environ.get("JQUANTS_PASSWORD")
    
    if not email or not password:
        print("警告: 環境変数 JQUANTS_EMAIL または JQUANTS_PASSWORD が設定されていません")
        print("テストを実行する前に、以下のコマンドで環境変数を設定してください:")
        print("export JQUANTS_EMAIL='your_email@example.com'")
        print("export JQUANTS_PASSWORD='your_password'")
    else:
        print(f"JQUANTS_EMAIL: {email[:3]}...（セキュリティのため一部のみ表示）")
        print(f"JQUANTS_PASSWORD: {'*' * 8}（セキュリティのため非表示）")
    
    token_success = test_token_retrieval()
    
    if token_success:
        data_success = test_data_retrieval()
        
        if data_success:
            print("\n✅ すべてのテストが成功しました！")
        else:
            print("\n❌ データ取得テストが失敗しました")
    else:
        print("\n❌ トークン取得テストが失敗しました")
