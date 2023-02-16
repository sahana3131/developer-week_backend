import requests

def test():
    response = requests.get("http://localhost:8001/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

if __name__ == "__main__":
    test()