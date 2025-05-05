"""
J-Quants API株価データ取得テスト
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta


# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from utils.jquants_api import get_refresh_token, get_id_token

def test_stock_data():
    """株価データ取得のテスト"""
    print("=== J-Quants API株価データ取得テスト ===")
    
    try:
        refresh_token = get_refresh_token()
        print(f"✅ リフレッシュトークン取得成功: {refresh_token[:10]}...（セキュリティのため一部のみ表示）")
        
        id_token = get_id_token(refresh_token)
        print(f"✅ IDトークン取得成功: {id_token[:10]}...（セキュリティのため一部のみ表示）")
        
        print("\n株価データ取得テスト")
        
        test_codes = ["1301", "7203", "9984"]
        
        from_date = "2023-03-01"
        to_date = "2023-03-31"
        
        for code in test_codes:
            print(f"\n証券コード: {code}")
            
            url = "https://api.jquants.com/v1/prices/daily_quotes"
            headers = {"Authorization": f"Bearer {id_token}"}
            params = {
                "code": code,
                "from": from_date,
                "to": to_date
            }
            
            print(f"リクエストURL: {url}")
            print(f"リクエストパラメータ: {params}")
            
            import requests
            res = requests.get(url, headers=headers, params=params)
            print(f"ステータスコード: {res.status_code}")
            
            try:
                data_json = res.json()
                print(f"レスポンスキー: {list(data_json.keys())}")
                
                data = data_json.get("daily_quotes", [])
                if data:
                    print(f"✅ データ取得成功！件数: {len(data)}")
                    if len(data) > 0:
                        print(f"最初のデータ: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ データが空です")
                    print(f"レスポンス: {json.dumps(data_json, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"❌ レスポンス処理エラー: {e}")
                print(f"レスポンス: {res.text}")
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_stock_data()
    
    if success:
        print("\n✅ テスト完了")
    else:
        print("\n❌ テスト失敗")
    
    if "JQUANTS_EMAIL" in os.environ:
        del os.environ["JQUANTS_EMAIL"]
    if "JQUANTS_PASSWORD" in os.environ:
        del os.environ["JQUANTS_PASSWORD"]
