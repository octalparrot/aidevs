import requests
import openai
import re
from decouple import config

# Ustawienia
apikey = config('API_KEY')
BASE_URL = "https://zadania.aidevs.pl"
openai_api_key = config('OPENAI_API_KEY')

# Ustaw klucz API OpenAI
openai.api_key = openai_api_key

def get_token():
    response = requests.post(
        f"{BASE_URL}/token/whisper",
        json={"apikey": apikey}
    )
    return response.json()["token"] if response.status_code == 200 else None

def get_audio_url(token):
    response = requests.get(f"{BASE_URL}/task/{token}")
    if response.status_code == 200:
        data = response.json()
        audio_message = data['msg']
        audio_url_match = re.search(r'(https?://\S+)', audio_message)
        if audio_url_match:
            return audio_url_match.group(0)  # Zwraca URL pliku audio
    else:
        print(f"Error: {response.status_code} - {response.text}")
    return None


def download_audio_file(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as audio_file:
            audio_file.write(response.content)
    return path if response.status_code == 200 else None
def transcribe_audio(path):
    try:
        with open(path, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe("whisper-1", audio_file)
        # Wydrukuj całą odpowiedź, aby sprawdzić jej zawartość
        print(transcript_response)
        # Oczekujemy, że odpowiedź będzie zawierała klucz 'text' z transkrypcją
        transcript = transcript_response.get('text', None)
        return transcript
    except Exception as e:
        print(f"Transcription error: {e}")
        return None


def submit_answer(token, answer):
    response = requests.post(
        f"{BASE_URL}/answer/{token}",
        json={"answer": answer}
    )
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    token = get_token()
    if token:
        audio_url = get_audio_url(token)
        if audio_url:
            audio_path = download_audio_file(audio_url, "audio.mp3")
            if audio_path:
                transcription = transcribe_audio(audio_path)
                if transcription is not None:  # Zmiana tutaj
                    print("Transcription successful!")  # Możesz dodać tę linię
                    result = submit_answer(token, transcription)
                    print("Transcription submitted:", result)
                else:
                    print("Failed to transcribe audio.")
            else:
                print("Failed to download audio file.")
        else:
            print("Failed to get audio URL.")
    else:
        print("Failed to get token.")
