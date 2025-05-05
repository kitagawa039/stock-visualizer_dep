import os
import requests

def get_jquants_token():
    email = os.environ["JQUANTS_EMAIL"]
    password = os.environ["JQUANTS_PASSWORD"]
    url = "https://api.jquants.com/v1/token/auth_user"
    res = requests.post(url, json={"mailaddress": email, "password": password})
    res.raise_for_status()
    print("J-Quants認証レスポンス:", res.json())
    return res.json().get("idToken")

if __name__ == "__main__":
    token = get_jquants_token()
    print("idToken:", token) 