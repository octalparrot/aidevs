import requests
import json
from decouple import config
import openai  # Dodano import modułu openai
from datetime import datetime

apikey = config('API_KEY')
openai_api_key = config('OPENAI_API_KEY')  # Klucz API OpenAI
openai.api_key = openai_api_key  # Ustawienie klucza API OpenAI na początku skryptu

BASE_URL = "https://zadania.aidevs.pl"

def get_token(tools_value):
    response = requests.post(
        f"{BASE_URL}/token/{tools_value}",
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

def submit_answer(token, decision):
    # Konwertowanie odpowiedzi na format wymagany przez API
    answer_payload = {"answer": decision}
    
    # Wyświetlanie JSONa przed wysłaniem
    print("Wysyłany JSON:", json.dumps(answer_payload, indent=4))

    response = requests.post(
        f"{BASE_URL}/answer/{token}",
        json=answer_payload  # Używamy zmodyfikowanego obiektu JSON
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def decide_task_type(task):
    try:
        # Uzyskanie dzisiejszej daty
        today_date = datetime.now().strftime("%Y-%m-%d")

        # Tworzenie sesji chat z GPT-4
        response = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[
              {"role": "system", "content": f"Today's date is {today_date}. Decide if the task should be added to the ToDo list or to the Calendar. If to the Calendar, provide a date in YYYY-MM-DD format according to today's date. If to the ToDo list, just state 'ToDo'.\n\nReply in JSON:\n{{\"tool\":\"ToDo\",\"desc\":\"\" }}\nor\n{{\"tool\":\"Calendar\",\"desc\":\"\",\"date\":\"\"}}"},
              {"role": "user", "content": f"{task}"}
          ]
        )
        decision_text = response['choices'][0]['message']['content']

        # Interpretowanie odpowiedzi JSON
        decision_json = json.loads(decision_text)
        return decision_json
    except Exception as e:
        print(f"Error while using OpenAI API: {e}")
        return None



if __name__ == "__main__":
    tools_value = "tools"  # Stała wartość
    token = get_token(tools_value)

    if token:
        print(f"Uzyskany token: {token}")
        task_data = get_task_data(token)

        if task_data:
            print("Dane zadania:", task_data)
            task = task_data.get('question')
            decision = decide_task_type(task)

            if decision:
                print("Decyzja GPT-4:", decision)
                result = submit_answer(token, decision)
                print("Odpowiedź serwera:", result)
            else:
                print("Nie udało się podjąć decyzji dla zadania.")
