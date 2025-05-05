

read -p "J-Quants メールアドレス: " email
read -sp "J-Quants パスワード: " password
echo

export JQUANTS_EMAIL="$email"
export JQUANTS_PASSWORD="$password"

echo "環境変数を設定しました。"
echo "JQUANTS_EMAIL=${email}"
echo "JQUANTS_PASSWORD=********"
