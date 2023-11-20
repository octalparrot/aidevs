import requests
import json
import openai
from packaging import version
from decouple import config
from openai import OpenAI

# Konfiguracja kluczy API
apikey = config('API_KEY')
openai_api_key = config('OPENAI_API_KEY')  # Klucz API OpenAI
BASE_URL = "https://zadania.aidevs.pl"

# Funkcje do interakcji z API serwisu
def get_token():
    try:
        response = requests.post(
            f"{BASE_URL}/token/gnome",
            json={"apikey": apikey}
        )
        response.raise_for_status()  # Sprawdza, czy nie wystąpił kod błędu HTTP
        token = response.json().get("token")
        print("Otrzymany token:", token)  # Wyświetla pobrany token
        return token
    except requests.RequestException as e:
        print(f"Error getting token: {e}")
        return None

def get_task_data(token):
    try:
        response = requests.get(f"{BASE_URL}/task/{token}")
        response.raise_for_status()
        task_data = response.json()
        print("Otrzymane zadanie od API:", json.dumps(task_data, indent=4))  # Wyświetla całe otrzymane zadanie
        return task_data
    except requests.RequestException as e:
        print(f"Error getting task data: {e}")
        return None

def submit_answer(token, answer):
    answer_json = {"answer": answer}
    print("JSON przygotowany do odpowiedzi:", json.dumps(answer_json, indent=4))  # Wyświetla JSON przygotowany do odpowiedzi
    try:
        response = requests.post(
            f"{BASE_URL}/answer/{token}",
            json=answer_json
        )
        response.raise_for_status()
        print("Odpowiedź serwera:", response.json())  # Wyświetla odpowiedź serwera
        return response.json()
    except requests.RequestException as e:
        print(f"Error submitting answer: {e}")
        return None

def analyze_image_with_gpt4_vision(image_url):
    client = OpenAI(api_key=openai_api_key)

    try:
        response = client.chat.completions.create(
          model="gpt-4-vision-preview",
          messages=[
            {
              "role": "user",
              "content": [
                {"type": "text", "text": "Jeżeli to jest skrzat, to jakiego koloru ma czapkę? Jeżeli nie jako odpowiedź daj 'error'"},
                {
                  "type": "image_url",
                  "image_url": {"url": image_url},
                },
              ],
            }
          ],
          max_tokens=300,
        )

        # Tworzenie i wyświetlanie sformatowanego JSON z odpowiedzi
        response_data = {
            "id": response.id,
            "model": response.model,
            "choices": [{"message": choice.message.content} for choice in response.choices]
        }
        print("Pełna odpowiedź od GPT-4 Vision:", json.dumps(response_data, indent=4))

        hat_color = response.choices[0].message.content.strip()
        return hat_color
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return "ERROR"


if __name__ == "__main__":
    token = get_token()

    if token:
        task_data = get_task_data(token)
        if task_data:
            image_url = task_data.get('url')
            if image_url:
                hat_color = analyze_image_with_gpt4_vision(image_url)

                if hat_color != "ERROR":
                    print(f"Submitting hat color: {hat_color}")
                    result = submit_answer(token, hat_color)
                else:
                    print("Error processing the image with GPT-4 Vision.")
            else:
                print("No image URL in the task data.")
        else:
            print("Failed to retrieve task data.")
    else:
        print("Failed to obtain the token.")
