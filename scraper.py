import requests
import openai
from decouple import config
import time
import json

# Ustawienia
try:
    apikey = config('API_KEY')
    BASE_URL = "https://zadania.aidevs.pl"
    openai_api_key = config('OPENAI_API_KEY')
except Exception as e:
    print(f"Błąd podczas pobierania konfiguracji: {e}")
    exit()

openai.api_key = openai_api_key

def get_token():
    try:
        response = requests.post(
            f"{BASE_URL}/token/scraper",
            json={"apikey": apikey}
        )
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        print(f"Błąd podczas pobierania tokena: {e}")
        return None

def get_task_data(token):
    try:
        response = requests.post(
            f"{BASE_URL}/task/{token}"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Błąd podczas pobierania danych zadania: {e}")
        return None

def submit_answer(token, answer, max_retries=5):
    retry_wait = 1  # początkowy czas oczekiwania w sekundach
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{BASE_URL}/answer/{token}",
                json={"answer": answer}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Błąd podczas wysyłania odpowiedzi (próba {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"Oczekiwanie {retry_wait} sekund(y) przed ponowieniem próby...")
                time.sleep(retry_wait)
                retry_wait *= 2  # podwajamy czas oczekiwania przy każdej kolejnej próbie
            else:
                print("Osiągnięto limit prób wysyłania odpowiedzi.")
                return None


def generate_answer(input_data, question):
    try:
        print("Przygotowanie wiadomości do modelu GPT...")
        # Dodanie instrukcji dla modelu GPT.
        system_message = f"Odpowiadaj krótko, w dwóch zdaniach na podstawie poniższego tekstu:\n{input_data}"
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]

        print("Wysyłanie wiadomości do modelu GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200
        )
        answer = response['choices'][0]['message']['content']
        # Sprawdzenie, czy odpowiedź składa się z dwóch zdań.
        sentences = [sentence.strip() for sentence in answer.split('.') if sentence]
        if len(sentences) > 2:
            answer = '. '.join(sentences[:2]) + '.'
        return answer.strip()
    except Exception as e:
        print(f"Błąd podczas generowania odpowiedzi przez GPT: {e}")
        return None


def fetch_data_with_retry(url, headers, max_retries=5):
    backoff_time = 1  # Start with 1 second of wait time
    for i in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500 and i < max_retries - 1:
                print(f"Błąd serwera (próba {i+1}): {e}, ponawiam za {backoff_time}s...")
                time.sleep(backoff_time)
                backoff_time *= 2  # Eksponencjalny wzrost czasu oczekiwania
                if backoff_time > 30:
                    backoff_time = 30  # Maksymalny czas oczekiwania to 30 sekund
            else:
                print(f"Błąd HTTP: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Nieznany błąd: {e}")
            return None
    return None

if __name__ == "__main__":
    print("Pobieranie tokena...")
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        print("Pobieranie danych zadania...")
        task_data = get_task_data(token)
        if task_data:
            input_data = task_data.get('input', '')
            question = task_data.get('question', '')
            print(f"Otrzymane pytanie: {question}")
            if 'http' in input_data:
                print(f"Próba pobrania danych z URL: {input_data}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                input_data = fetch_data_with_retry(input_data, headers)
                if input_data:
                    print("Dane pobrane pomyślnie.")
                else:
                    print("Nie udało się pobrać danych po maksymalnej liczbie prób.")
                    exit()

            print("Generowanie odpowiedzi...")
            answer = generate_answer(input_data, question)
            if answer:
                print(f"Wygenerowana odpowiedź: {answer}")
                print("Wysyłanie odpowiedzi...")
                result = submit_answer(token, answer)
                print("Odpowiedź serwera:", result)
            else:
                print("Nie udało się wygenerować odpowiedzi.")
        else:
            print("Nie można było pobrać danych zadania.")
    else:
        print("Nie udało się uzyskać tokena.")
