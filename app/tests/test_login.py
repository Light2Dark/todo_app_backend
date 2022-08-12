import requests
import json

def login(email: str, password: str):
    body = {
        "email": email,
        "password": password
    }
    response = requests.post("http://localhost:8000/login", json=body)
    return json.loads(response.text)["token"] # return just the token

token = login("test123@gmail.com", "test123")
print(token)


# using ping endpoint for jwt validation
def ping(token: str):
    headers = {
        "authorization": token
    }
    response = requests.post("http://localhost:8000/ping", headers=headers)
    return response.text

print(ping(token))