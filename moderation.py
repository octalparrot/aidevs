import requests
import json
import openai
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
openai_api_key = config('OPENAI_API_KEY')

openai.api_key = openai_api_key

def get_token():
    response = requests.post(
        f"{BASE_URL}/token/moderation",
        json={"apikey": apikey}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_sentences(token):
    response = requests.get(
        f"{BASE_URL}/task/{token}"
    )
    if response.status_code == 200:
        return response.json()['input']
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

def moderate_sentences(sentences):
    moderation_results = []
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    for sentence in sentences:
        try:
            response = requests.post(
                "https://api.openai.com/v1/moderations",
                headers=headers,
                data=json.dumps({"input": sentence})
            )
            # Dodajemy instrukcje drukowania, aby zobaczyć odpowiedź z API oraz status HTTP
#            print(f"HTTP Status Code: {response.status_code}")
#            print(f"API Response: {response.json()}")
            
            response_json = response.json()
            flagged = response_json['results'][0]['flagged']
            moderation_results.append(1 if flagged else 0)
        except Exception as e:
            print(f"Error: {e}")
            moderation_results.append(0)  # Zakładamy, że zdanie nie przeszło moderacji w przypadku błędu
    return moderation_results


if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        
        # Pobierz zdania z API
        sentences = get_sentences(token)
        if sentences:
            print(f"Received sentences: {sentences}")
            
            moderation_results = moderate_sentences(sentences)
            print(f"Moderation results: {moderation_results}")
            
            result = submit_answer(token, moderation_results)
            print("Server response:", result)
        else:
            print("Could not retrieve sentences.")
