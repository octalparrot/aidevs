# main.py
import requests
from decouple import config

apikey = config('API_KEY')

BASE_URL = "https://zadania.aidevs.pl"

def get_token(helloapi):
    response = requests.post(
        f"{BASE_URL}/token/{helloapi}",
        json={"apikey": apikey}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_task_data(token):
    response = requests.get(f"{BASE_URL}/task/{token}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def submit_answer(token, answer):
    response = requests.post(
        f"{BASE_URL}/answer/{token}",
        json={"answer": answer}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    helloapi_value = input("Podaj wartość dla zdania: ")
    token = get_token(helloapi_value)
    
    if token:
        task_data = get_task_data(token)
        print("Dane zadania:", task_data)

        answer = input("Wprowadź swoją odpowiedź: ")
        result = submit_answer(token, answer)
        print("Odpowiedź serwera:", result)
