from flask import Flask, request, jsonify
from openai import OpenAI
import os
import io
import base64
from datetime import datetime

app = Flask(__name__)


upload_count = 0

def upload_image_to_openai(image_stream):
    # Read the image from the stream and encode it to base64
    image_data = image_stream.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    client = OpenAI()

    # Construct the image URL payload
    image_url_payload = {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
        }
    }

    client = OpenAI()

    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": """ You are an image recognition model. Identify if the object is a plastic bottle, glass bottle, or neither. 
- Plastic bottle: flexible, translucent, with a visible cap.
- Glass bottle: rigid, shiny, often thicker, and transparent.
Respond with "plastic bottle", "glass bottle", or "not found """
            }
          ]
        },
        {
          "role": "user",
          "content": [
              {
                  "type": "text",
                  "text": """Is the object in the image a plastic bottle?"""
              },
              image_url_payload
          ]
        }
      ],
      temperature=1,
      max_tokens=4095,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
    return response.choices[0].message.content


# @app.route('/upload', methods=['POST'])
# def upload():
#     global upload_count
#     file = request.files['image']
    
#     if file:
#         image_stream = io.BytesIO(file.read())
#         result = upload_image_to_openai(image_stream)
#         upload_count += 1
        
#         # Check the content of the result
#         if "plastic" in result.lower():
#             response = "plastic bottle"
#         elif "glass" in result.lower():
#             response = "glass bottle"
#         else:
#             response = "not found"
        
#         return jsonify({'result': response, 'upload_count': upload_count})
    
#     return jsonify({'error': 'No image uploaded'}), 400

@app.route('/upload', methods=['POST'])
def upload():
    global upload_count

    print("Headers:", request.headers)  # Log the incoming headers
    print("Data Length:", len(request.data))  # Log the length of the incoming data

    file = request.files['image']
    
    if file:
        image_stream = io.BytesIO(file.read())
        result = upload_image_to_openai(image_stream)
        upload_count += 1
        
        # Check the content of the result
        if "plastic" in result.lower():
            response = "plastic bottle"
        elif "glass" in result.lower():
            response = "glass bottle"
        else:
            response = "not found"
        
        return response, 200  # Return plain text with a 200 status code
    
    return "No image uploaded", 400  # Return plain text error message


@app.route('/upload2', methods=['POST'])
def upload2():
    global upload_count

    print("Headers:", request.headers)  # Log the incoming headers
    print("Data Length:", len(request.data))  # Log the length of the incoming data

    file = request.files['image']
    
    if file:
        # Create the uploads directory if it doesn't exist
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # Generate a filename with a datetime stamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(uploads_dir, filename)

        # Save the file locally
        file.save(filepath)

        image_stream = io.BytesIO(file.read())
        upload_count += 1
        
        # # Check the content of the result
        # if "plastic" in result.lower():
        #     response = "plastic bottle"
        # elif "glass" in result.lower():
        #     response = "glass bottle"
        # else:
        #     response = "not found"

        response = "image saved"
        
        return response, 200  # Return plain text with a 200 status code
    
    return "No image uploaded", 400  # Return plain text error message

@app.route('/test', methods=['POST'])
def test():
    global upload_count
    file = request.files['image']
    
    if file:
        image_stream = io.BytesIO(file.read())
        upload_count += 1
        response = "good"
        return response, 200  # Return plain text with a 200 status code
    
    return "No image uploaded", 400  # Return plain text error message

@app.route('/good', methods=['GET'])
def good():
    return "good", 200  # Return plain text "good" with a 200 status code


@app.route('/count', methods=['GET'])
def count():
    return jsonify({'upload_count': upload_count})

@app.route('/', methods=['GET'])
def home():
    return "Server is running"

if __name__ == '__main__':
    app.run(debug=True)
