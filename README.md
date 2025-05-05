# Stock Visualizer 📈

株価データを可視化するWebアプリケーションです。日本株（J-Quants）と米国株（Alpha Vantage）のデータを表示し、テクニカル分析や投資信託のパフォーマンス分析が可能です。

## 機能

### 株式チャート
- 日本株（J-Quants）と米国株（Alpha Vantage）の表示
- ローソク足チャート
- 移動平均線（5日、25日、75日）
- 出来高表示
- RSI（相対力指数）
- ボラティリティ分析
- データテーブル表示とCSVダウンロード

### 投資信託特設ページ
- 人気投資信託の基準価額推移
- パフォーマンス分析
- 月次リターン表示
- データテーブル表示とCSVダウンロード

## 技術スタック

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- J-Quants API
- Alpha Vantage API

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/stock-visualizer.git
cd stock-visualizer
```

2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

3. 環境変数の設定
```bash
# J-Quants API
export JQUANTS_EMAIL="your_email@example.com"
export JQUANTS_PASSWORD="your_password"

# Alpha Vantage API
export ALPHAVANTAGE_API_KEY="your_api_key"
```

## ローカルでの実行

```bash
streamlit run src/app.py
```

## デプロイ

このアプリケーションはStreamlit Cloudでデプロイできます。

1. GitHubリポジトリをStreamlit Cloudに連携
2. 以下の環境変数を設定：
   - `JQUANTS_EMAIL`
   - `JQUANTS_PASSWORD`
   - `ALPHAVANTAGE_API_KEY`
3. メインファイルのパスを`src/app.py`に設定
4. デプロイを実行

## ライセンス

MITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 注意事項

- J-Quants APIとAlpha Vantage APIの利用規約に従ってください
- このアプリケーションは投資助言を目的としていません
- 表示されるデータは参考情報としてご利用ください
