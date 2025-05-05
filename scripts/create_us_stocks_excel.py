import pandas as pd
import os
from pathlib import Path

# プロジェクトのルートディレクトリを取得
project_root = Path(__file__).parent.parent
data_dir = project_root / 'data'

# データディレクトリが存在しない場合は作成
data_dir.mkdir(exist_ok=True)

# アメリカ株のデータ
US_STOCKS = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services"},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail"},
    "META": {"name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Internet Services"},
    "TSLA": {"name": "Tesla Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banks"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    "V": {"name": "Visa Inc.", "sector": "Financial Services", "industry": "Credit Services"},
    "PG": {"name": "Procter & Gamble Co.", "sector": "Consumer Defensive", "industry": "Household Products"},
    "UNH": {"name": "UnitedHealth Group Inc.", "sector": "Healthcare", "industry": "Healthcare Plans"},
    "HD": {"name": "Home Depot Inc.", "sector": "Consumer Cyclical", "industry": "Home Improvement Retail"},
    "BAC": {"name": "Bank of America Corp.", "sector": "Financial Services", "industry": "Banks"},
    "MA": {"name": "Mastercard Inc.", "sector": "Financial Services", "industry": "Credit Services"}
}

# DataFrameの作成
df = pd.DataFrame([
    {
        "ティッカーシンボル": ticker,
        "会社名": data["name"],
        "セクター": data["sector"],
        "業種": data["industry"]
    }
    for ticker, data in US_STOCKS.items()
])

# Excelファイルとして保存
output_path = data_dir / 'data_us.xlsx'
df.to_excel(output_path, index=False)
print(f"アメリカ株のデータをExcelファイルに保存しました: {output_path}") 