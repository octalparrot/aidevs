import requests
import openai
from decouple import config
import re

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
openai_api_key = config('OPENAI_API_KEY')

openai.api_key = openai_api_key

def get_token():
    response = requests.post(
        f"{BASE_URL}/token/inprompt",
        json={"apikey": apikey}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_task_data(token):
    response = requests.post(
        f"{BASE_URL}/task/{token}"
    )
    if response.status_code == 200:
        data = response.json()
#        print(f"Task data: {data}")  # Add this line
        return data
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

def extract_name(question):
    # Assume the name will be a single word starting with a capital letter.
    match = re.search(r'\b[A-Z][a-z]*\b', question)
    return match.group(0) if match else None


def generate_answer(question, relevant_sentences):
    try:
        # Prepare the messages for the ChatCompletion endpoint
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": ' '.join(relevant_sentences)},
            {"role": "user", "content": question}
        ]

        # Now send this messages to the model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        task_data = get_task_data(token)
        if task_data:
            sentences = task_data.get('input', [])
            question = task_data.get('question', '')
            print(f"Question: {question}")  # This line will print the question
            name = extract_name(question)
            relevant_sentences = [s for s in sentences if name in s]
            print(f"Relevant sentences: {relevant_sentences}")  # Add this line
            answer = generate_answer(question, relevant_sentences)
            print(f"Generated answer: {answer}")  # Add this line
            if answer:
                result = submit_answer(token, answer)
                print("Server response:", result)
            else:
                print("Could not generate an answer.")
        else:
            print("Could not get task data.")
