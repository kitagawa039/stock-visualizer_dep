"""
J-Quants API認証フロー更新版テスト
"""
import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

EMAIL = os.environ.get("JQUANTS_EMAIL")
PASSWORD = os.environ.get("JQUANTS_PASSWORD")

def test_auth_flow():
    """J-Quants APIの認証フローをテストする関数"""
    print("=== J-Quants API認証フロー更新版テスト ===")
    
    if not EMAIL or not PASSWORD:
        print("❌ 環境変数 JQUANTS_EMAIL または JQUANTS_PASSWORD が設定されていません")
        return False
    
    print("\n1. リフレッシュトークン取得")
    try:
        auth_url = "https://api.jquants.com/v1/token/auth_user"
        auth_payload = {"mailaddress": EMAIL, "password": PASSWORD}
        
        auth_res = requests.post(auth_url, json=auth_payload)
        auth_res.raise_for_status()
        
        auth_json = auth_res.json()
        print(f"ステータスコード: {auth_res.status_code}")
        print(f"レスポンスキー: {list(auth_json.keys())}")
        
        refresh_token = auth_json.get("refreshToken")
        if not refresh_token:
            print("❌ リフレッシュトークン取得失敗: refreshTokenがレスポンスに含まれていません")
            print(f"レスポンス: {json.dumps(auth_json, indent=2, ensure_ascii=False)}")
            return False
            
        print(f"✅ リフレッシュトークン取得成功: {refresh_token[:10]}...（セキュリティのため一部のみ表示）")
        
        print("\n2. IDトークン取得")
        id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
        params = {"refreshtoken": refresh_token}
        
        id_token_res = requests.post(id_token_url, params=params)
        id_token_res.raise_for_status()
        
        id_token_json = id_token_res.json()
        print(f"ステータスコード: {id_token_res.status_code}")
        print(f"レスポンスキー: {list(id_token_json.keys())}")
        
        id_token = id_token_json.get("idToken")
        if not id_token:
            print("❌ IDトークン取得失敗: idTokenがレスポンスに含まれていません")
            print(f"レスポンス: {json.dumps(id_token_json, indent=2, ensure_ascii=False)}")
            return False
            
        print(f"✅ IDトークン取得成功: {id_token[:10]}...（セキュリティのため一部のみ表示）")
        
        print("\n3. 株価データ取得")
        symbol = "7203"  # トヨタ自動車の証券コード
        
        from_date = "2023-01-01"
        to_date = "2023-01-31"
        
        data_url = "https://api.jquants.com/v1/prices/daily_quotes"
        headers = {"Authorization": f"Bearer {id_token}"}
        params = {
            "code": symbol,
            "from": from_date,
            "to": to_date
        }
        
        print(f"リクエストパラメータ: {params}")
        
        data_res = requests.get(data_url, headers=headers, params=params)
        data_res.raise_for_status()
        
        data_json = data_res.json()
        print(f"ステータスコード: {data_res.status_code}")
        print(f"レスポンスキー: {list(data_json.keys())}")
        
        data = data_json.get("daily_quotes", [])
        if not data:
            print("❌ データ取得失敗: データが空です")
            print(f"レスポンス: {json.dumps(data_json, indent=2, ensure_ascii=False)}")
            return False
        
        print(f"✅ データ取得成功！件数: {len(data)}")
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
        
        print("\nデータサンプル:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    if not EMAIL or not PASSWORD:
        print("環境変数を設定してください:")
        print("export JQUANTS_EMAIL='your_email@example.com'")
        print("export JQUANTS_PASSWORD='your_password'")
    else:
        success = test_auth_flow()
        
        if success:
            print("\n✅ すべてのテストが成功しました！")
        else:
            print("\n❌ テストが失敗しました")
