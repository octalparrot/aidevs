import requests
import json
from decouple import config

# Stała wartość dla helloapi_value
helloapi_value = "optimaldb"

# Pobieranie klucza API z konfiguracji
apikey = config('API_KEY')

# Bazowy adres URL API
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
    token = get_token(helloapi_value)

    if token:
        print(f"Uzyskany token: {token}")
        task_data = get_task_data(token)
        print("Dane zadania:", task_data)

        # Wczytanie zoptymalizowanej bazy danych jako string
        with open('3friendsoptimal.json', 'r') as file:
            optimal_db_string = file.read()

        # Wysłanie zoptymalizowanej bazy danych jako odpowiedź
        result = submit_answer(token, optimal_db_string)
        print("Odpowiedź serwera:", result)
