import pandas as pd
from pathlib import Path

# プロジェクトのルートディレクトリを取得
project_root = Path(__file__).parent.parent
data_dir = project_root / 'data'

# Excelファイルを読み込む
df = pd.read_excel(data_dir / 'data_j.xlsx')

# 最初の5行を表示
print("最初の5行:")
print(df.head())

# カラム名を表示
print("\nカラム名:")
print(df.columns.tolist())

# データの基本情報を表示
print("\nデータの基本情報:")
print(df.info()) 