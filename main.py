from flask import Flask, request, jsonify
import openai
import os
import io

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

upload_count = 0

def upload_image_to_openai(image_stream):
    system_prompt = """You are an image recognition model. Identify if the object is a plastic bottle, glass bottle, or neither."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Is the object in the image a plastic bottle?"}
        ]
    )
    
    return response['choices'][0]['message']['content']

@app.route('/upload', methods=['POST'])
def upload():
    global upload_count
    file = request.files['image']
    
    if file:
        image_stream = io.BytesIO(file.read())
        result = upload_image_to_openai(image_stream)
        upload_count += 1
        return jsonify({'result': result, 'upload_count': upload_count})
    return jsonify({'error': 'No image uploaded'}), 400

@app.route('/count', methods=['GET'])
def count():
    return jsonify({'upload_count': upload_count})


@app.route('/', methods=['GET'])
def home():
    return "Server is running"

if __name__ == '__main__':
    app.run(debug=True)
