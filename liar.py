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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Question: {question}\nAnswer: {answer}\nIs the provided answer accurate and relevant to the question?"}
            ]
        )
        result = response['choices'][0]['message']['content'].strip().upper()
        return "YES" if result == "YES" else "NO"
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


def generate_question():
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt="Generate a question:",
            max_tokens=15,
            temperature=0.7
        )
        question = response['choices'][0]['text'].strip()
        return question
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        # Generuj pytanie za pomocą API OpenAI
        question = generate_question()
        if question:
            print(f"Generated question: {question}")
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
        else:
            print("Could not generate a question.")
