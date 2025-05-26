import os
import json
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

API_KEY = "YOUR_API_KEY"
client = Groq(api_key=API_KEY)

DOCUMENTS_DIR = "document_store/txts/"

def load_documents():
    """Nạp dữ liệu từ các file .txt và ghép nội dung thành một chuỗi lớn."""
    documents = []
    for filename in os.listdir(DOCUMENTS_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(DOCUMENTS_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                documents.append(file.read().strip()) 
    return "\n".join(documents)

CONTEXT_TEXT = load_documents()

def generate_answer(user_query):
    """Gửi truy vấn đến Groq API và tạo câu trả lời dựa trên ngữ cảnh."""
    full_prompt = f"{CONTEXT_TEXT}\nCâu hỏi của người dùng: {user_query}\nCâu trả lời:"

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama-3.3-70b-versatile",
        )

        if chat_completion.choices and len(chat_completion.choices) > 0:
            return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"Lỗi khi gọi API Groq: {e}")
    
    return "Xin lỗi, hiện tại tôi không thể trả lời câu hỏi này."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'Vui lòng nhập câu hỏi.'})
    
    response = generate_answer(message)

    return Response(json.dumps({'response': response}, ensure_ascii=False), content_type="application/json; charset=utf-8")

if __name__ == '__main__':
    app.run(debug=True)
