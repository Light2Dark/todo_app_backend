import requests

def signup(email: str, password: str):
    body = {
        "email": email,
        "password": password
    }
    response = requests.post("http://localhost:8000/signup", json=body)
    return response.text

print(signup("test123@gmail.com", "test123"))