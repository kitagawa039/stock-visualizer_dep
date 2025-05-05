import requests
import os

email = os.environ["JQUANTS_EMAIL"]
password = os.environ["JQUANTS_PASSWORD"]

res = requests.post("https://api.jquants.com/v1/token/auth_user", json={
    "mailaddress": email,
    "password": password
})
print(res.status_code, res.text) 