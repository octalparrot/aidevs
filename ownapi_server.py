# ownapi_server.py
from flask import Flask, request, jsonify
from openai import OpenAI
from decouple import config

app = Flask(__name__)

openai_api_key = config('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

conversation_history = []

def get_gpt4_response(question):
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Odpowiedz krótko, ale najlepiej jak potrafisz."},
                {"role": "user", "content": question}
            ]
        )
        # Uzyskanie odpowiedzi z obiektu chat_completion
        print(chat_completion)  # Tymczasowy wydruk do debugowania
        return chat_completion.choices[0].message.content
    except Exception as e:
        return str(e)


@app.route('/', methods=['POST'])
def answer_question():
    data = request.get_json()

    if isinstance(data, dict) and "question" in data:
        question = data["question"]
        answer = get_gpt4_response(question)
        return jsonify({"reply": answer})
    else:
        return jsonify({"error": "Invalid input format"}), 400

if __name__ == '__main__':
    app.run(port=5000)
