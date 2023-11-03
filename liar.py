import requests
import random
import openai
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
openai_api_key = config('OPENAI_API_KEY')

openai.api_key = openai_api_key

def get_token():
    response = requests.post(
        f"{BASE_URL}/token/liar",
        json={"apikey": apikey}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def send_question(token, question):
    response = requests.post(
        f"{BASE_URL}/task/{token}",
        data={"question": question}
    )
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

def evaluate_answer(question, answer):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Question: {question}\nAnswer: {answer}\nIs the answer correct?",
            max_tokens=10
        )
        result = response['choices'][0]['text'].strip().upper()
        return "YES" if result == "YES" else "NO"
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


# Lista pytań
questions = [
    "What is the capital of France?",
    "Is the sky blue?",
    "Do fish swim?",
    "Is water wet?",
    "Can birds fly?",
    "Is fire hot?",
    "Do dogs bark?",
    "Is ice cold?",
    "Can humans breathe underwater?",
    "Is the Earth round?"
]

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        # Wybierz losowe pytanie z listy
        question = random.choice(questions)
        print(f"Selected question: {question}")
        question_response = send_question(token, question)
        print("Server response:", question_response)
        
        server_answer = question_response.get('answer', '')
        truth_value = evaluate_answer(question, server_answer)
        print(f"Evaluation result: {truth_value}")
        
        if truth_value:
            result = submit_answer(token, truth_value)
            print("Server response:", result)
        else:
            print("Could not evaluate the answer.")
