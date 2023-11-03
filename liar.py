import requests
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"

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


if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")
        question = input("Enter your question in English: ")
        question_response = send_question(token, question)
        print("Server response:", question_response)
        
        truth_value = None
        while truth_value not in ["YES", "NO"]:
            truth_value = input("Is the answer true? (YES/NO): ").upper()
        result = submit_answer(token, truth_value)
        print("Server response:", result)
