"""
J-Quants API認証フローのみをテスト
"""
import os
import sys


# プロジェクトのルートディレクトリをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from utils.jquants_api import get_refresh_token, get_id_token

def test_auth_flow():
    """認証フローのみをテスト"""
    print("=== J-Quants API認証フローテスト ===")
    
    try:
        print("\n1. リフレッシュトークン取得")
        refresh_token = get_refresh_token()
        print(f"✅ リフレッシュトークン取得成功: {refresh_token[:10]}...（セキュリティのため一部のみ表示）")
        
        print("\n2. IDトークン取得")
        id_token = get_id_token(refresh_token)
        print(f"✅ IDトークン取得成功: {id_token[:10]}...（セキュリティのため一部のみ表示）")
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_flow()
    
    if success:
        print("\n✅ 認証フローテスト成功！")
    else:
        print("\n❌ 認証フローテスト失敗")
