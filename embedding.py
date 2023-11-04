import requests
import openai
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
openai_api_key = config('OPENAI_API_KEY')

openai.api_key = openai_api_key

def get_token():
    response = requests.post(
        f"{BASE_URL}/token/embedding",
        json={"apikey": apikey}
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def generate_embedding():
    try:
        response = openai.Embedding.create(input="Hawaiian pizza", model="text-embedding-ada-002")
        embedding = response['data'][0]['embedding']
        return embedding
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

def submit_answer(token, embedding):
    response = requests.post(
        f"{BASE_URL}/answer/{token}",
        json={"answer": embedding}
    )
    if response.status_code == 200:
        print("Successfully submitted the embedding.")
        return response.json()
    else:
        print(f"Error submitting the embedding: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    token = get_token()
    if token:
        print(f"Uzyskany token: {token}")

        embedding = generate_embedding()
        if embedding:
            # Make sure the embedding is the right length
            if len(embedding) == 1536:
                print("Generated embedding successfully.")
                result = submit_answer(token, embedding)
                print("Server response:", result)
            else:
                print(f"Error: The generated embedding length is {len(embedding)}, but it should be 1536.")
        else:
            print("Could not generate embedding.")
