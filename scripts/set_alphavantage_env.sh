
echo "Alpha Vantage API環境変数設定"
echo "----------------------------"

if [ -n "$ALPHAVANTAGE_API_KEY" ]; then
    echo "既存のAlpha Vantage APIキーが見つかりました: $ALPHAVANTAGE_API_KEY"
    read -p "このキーを使用しますか？ (y/n): " use_existing
    if [ "$use_existing" = "y" ]; then
        echo "既存のキーを使用します。"
        exit 0
    fi
fi

read -p "Alpha Vantage APIキーを入力してください (または空白でdemoキーを使用): " api_key

if [ -z "$api_key" ]; then
    api_key="demo"
    echo "demoキーを使用します。機能が制限される場合があります。"
fi

export ALPHAVANTAGE_API_KEY="$api_key"
echo "環境変数 ALPHAVANTAGE_API_KEY が設定されました: $ALPHAVANTAGE_API_KEY"
echo ""
echo "注意: この環境変数はこのターミナルセッションでのみ有効です。"
echo "永続的に設定するには、.bashrcや.bash_profileに追加してください。"
