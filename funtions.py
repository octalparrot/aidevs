# main.py
import requests
import json
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
helloapi_value = "functions"

# Definicja funkcji do pobrania tokena
def get_token(helloapi):
    response = requests.post(
        f"{BASE_URL}/token/{helloapi}",
        json={"apikey": apikey}
    )
    return response.json()["token"] if response.status_code == 200 else None

# Definicja funkcji do pobrania danych zadania
def get_task_data(token):
    response = requests.get(f"{BASE_URL}/task/{token}")
    return response.json() if response.status_code == 200 else None

# Definicja funkcji do wysyłania odpowiedzi
def submit_answer(token, answer):
    response = requests.post(
        f"{BASE_URL}/answer/{token}",
        json={"answer": answer}
    )
    return response.json() if response.status_code == 200 else None

# Główna część skryptu
if __name__ == "__main__":
    token = get_token(helloapi_value)

    if token:
        print(f"Uzyskany token: {token}")
        task_data = get_task_data(token)
        print("Dane zadania:", task_data)

        # Tworzenie odpowiedzi w formacie JSON
        answer = {
            "name": "addUser",
            "description": "adds a new user with given name, surname and year of birth",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "provide the first name of the user"
                    },
                    "surname": {
                        "type": "string",
                        "description": "provide the last name of the user"
                    },
                    "year": {
                        "type": "integer",
                        "description": "provide the year of birth of the user"
                    }
                }
            }
        }

        # Wysłanie odpowiedzi
        result = submit_answer(token, answer)
        print("Odpowiedź serwera:", result)
    else:
        print("Nie udało się uzyskać tokena.")
