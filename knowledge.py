import requests
import json
import re
import openai
from decouple import config

# Konfiguracja początkowa
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
HELLOAPI_VALUE = "knowledge"
openai.api_key = config('OPENAI_API_KEY')

# Funkcje do komunikacji z API
def get_token():
    response = requests.post(
        f"{BASE_URL}/token/{HELLOAPI_VALUE}",
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

def get_currency_rate(currency_code):
    try:
        response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/A/{currency_code}/?format=json")
        if response.status_code == 200:
            data = response.json()
            return data['rates'][0]['mid']
        else:
            print(f"Error: Nie udało się pobrać kursu dla waluty {currency_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def get_country_population(country_name):
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        if response.status_code == 200:
            data = response.json()
            return data[0]['population']
        else:
            print(f"Error: Nie udało się pobrać danych o populacji kraju {country_name}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def get_general_knowledge_answer(question):
    try:
        response = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[{"role": "system", "content": "Proszę bardzo krótko odpowiedzieć na poniższe pytanie."},
                    {"role": "user", "content": question}]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Błąd przy próbie uzyskania odpowiedzi: {e}")
        return "Nie mogłem uzyskać odpowiedzi."

def translate_country_name(question):
    try:
        # Użyj GPT-4 do przetłumaczenia nazwy kraju na angielski
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Translate the name of the country from Polish to English. Return only name of the country"},
                {"role": "user", "content": question}
            ]
        )
        translated_name = response.choices[0].message['content'].strip()
        return translated_name
    except Exception as e:
        print(f"Błąd przy próbie tłumaczenia nazwy kraju: {e}")
        return None

def translate_question_to_currency_iso(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Translate the following question about currency rate to a currency ISO code."},
                {"role": "user", "content": question}
            ]
        )
        currency_iso = response.choices[0].message['content'].strip()
        return currency_iso
    except Exception as e:
        print(f"Błąd przy próbie tłumaczenia pytania na kod ISO waluty: {e}")
        return None

def analyze_question(question):
    try:
        if 'kurs' in question.lower():
            currency_code = translate_question_to_currency_iso(question)
            if currency_code:
                currency_rate = get_currency_rate(currency_code)
                if currency_rate:
                    return {"question": question, "answer": currency_rate, "category": "Waluta"}  # Zwraca tylko kurs waluty
                else:
                    return {"question": question, "answer": "Brak kursu", "category": "Waluta"}
            else:
                return {"question": question, "answer": "Nie rozpoznano kodu waluty", "category": "Waluta"}

        elif 'populację' in question.lower() or 'populacja' in question.lower() or 'mieszka' in question.lower():
            translated_country_name = translate_country_name(question)
            if translated_country_name:
                population = get_country_population(translated_country_name)
                if population:
                    return {"question": question, "answer": population, "category": "Kraj"}  # Zwraca tylko liczbę populacji
                else:
                    return {"question": question, "answer": "Brak danych o populacji", "category": "Kraj"}
            else:
                return {"question": question, "answer": "Nie rozpoznano nazwy kraju", "category": "Kraj"}

        else:
            answer = get_general_knowledge_answer(question)
            return {"question": question, "answer": answer, "category": "Inne"}

    except Exception as e:
        print(f"Błąd przy próbie analizy pytania: {e}")
        return {"question": question, "answer_gpt": "error", "category": "error"}

def submit_answer(token, answer):
    try:
        response = requests.post(
            f"{BASE_URL}/answer/{token}",
            json={"answer": answer}
        )
        print(f"Wysłana odpowiedź: {answer}")
        if response.status_code == 200:
            print("Odpowiedź została pomyślnie zgłoszona.")
        else:
            print(f"Błąd przy zgłaszaniu odpowiedzi: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception: {e}")


# Główna pętla skryptu
if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        task_data = get_task_data(token)
        if task_data:
            question = task_data.get('question', 'Brak pytania')
            print(f"Otrzymane pytanie: {question}")  # Wyświetlenie pytania
            analysis = analyze_question(question)
            print(f"Analiza pytania: {json.dumps(analysis, indent=2, ensure_ascii=False)}")

            # Włączenie wysyłania odpowiedzi
            if 'answer' in analysis:
                submit_answer(token, analysis['answer'])
    else:
        print("Nie udało się uzyskać tokenu.")
