"""
J-Quants API最終テスト
"""
import os
import sys


project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from utils.jquants_api import get_stock_data

def test_get_stock_data():
    """株価データ取得のテスト"""
    print("=== J-Quants API株価データ取得最終テスト ===")
    
    try:
        print("\n1. デフォルトパラメータでのデータ取得")
        data = get_stock_data("7203")  # トヨタ自動車
        print(f"✅ データ取得成功！行数: {len(data)}")
        print("\nデータサンプル:")
        print(data.head())
        
        print("\n2. 日付範囲を指定したデータ取得")
        data = get_stock_data("9984", from_date="2023-03-01", to_date="2023-03-31")  # ソフトバンクグループ
        print(f"✅ データ取得成功！行数: {len(data)}")
        print("\nデータサンプル:")
        print(data.head())
        
        print("\n3. 証券コードに.Tが付いている場合")
        data = get_stock_data("1301.T", from_date="2023-03-01", to_date="2023-03-31")  # 極洋
        print(f"✅ データ取得成功！行数: {len(data)}")
        print("\nデータサンプル:")
        print(data.head())
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_get_stock_data()
    
    if success:
        print("\n✅ すべてのテストが成功しました！")
    else:
        print("\n❌ テストが失敗しました")
