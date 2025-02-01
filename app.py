from flask import Flask, request, jsonify, send_file
from openai import OpenAI
import os
import io
import base64
from PIL import Image
import http.client
import json
import requests


app = Flask(__name__)

latest_image = None
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
      model="gpt-4o-mini",
      messages=[
        {
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": """ You are an image recognition model. Identify if the object is a plastic bottle, glass bottle, or neither. 
- Plastic bottle: flexible, translucent, with a visible cap, with visible label.
- Glass bottle: rigid, shiny, often thicker, without label and transparent.
if image is in the dark return to "not found"
if bottle has cap return "not found"
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


# @app.route('/uploadxxx0', methods=['POST'])
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
    global upload_count, latest_image

    print("Headers:", request.headers)  # Log the incoming headers
    print("Data Length:", len(request.data))  # Log the length of the incoming data

    file = request.files['image']
    
    if file:
        image_stream = io.BytesIO(file.read())
        
        # Open the image and resize it to 30%
        image = Image.open(image_stream)
        new_size = (int(image.width * 0.9), int(image.height * 0.9))
        resized_image = image.resize(new_size, Image.LANCZOS)

        # Save the resized image to a new BytesIO stream
        resized_image_stream = io.BytesIO()
        resized_image.save(resized_image_stream, format=image.format)
        resized_image_stream.seek(0)  # Reset stream position to the beginning

        latest_image = resized_image_stream  # Store the resized image in memory
        result = upload_image_to_openai(resized_image_stream)
        upload_count += 1
        
        # Check the content of the result
        if "plastic" in result.lower():
            response = "plastic bottle"
        elif "glass" in result.lower():
            response = "not found"
        else:
            response = "not found"
        
        return response, 200  # Return plain text with a 200 status code
        # return "response", 200  # Return plain text with a 200 status code
    
    return "No image uploaded", 400  # Return plain text error message

# @app.route('/upload', methods=['POST'])
# def upload():
#     global upload_count, latest_image

#     print("Headers:", request.headers)  # Log the incoming headers
#     print("Data Length:", len(request.data))  # Log the length of the incoming data


#     file = request.files['image']
    
#     if file:
#         image_stream = io.BytesIO(file.read())
#         latest_image = image_stream  # Store the image in memory
#         result = upload_image_to_openai(image_stream)
#         upload_count += 1
        
#         # Check the content of the result
#         if "plastic" in result.lower():
#             response = "plastic bottle"
#         elif "glass" in result.lower():
#             response = "glass bottle"
#         else:
#             response = "not found"
        
#         return response, 200  # Return plain text with a 200 status code
    
#     return "No image uploaded", 400  # Return plain text error message


# @app.route('/upload2', methods=['POST'])
# def upload2():
#     global upload_count

#     print("Headers:", request.headers)  # Log the incoming headers
#     print("Data Length:", len(request.data))  # Log the length of the incoming data

#     file = request.files['image']
    
#     if file:
#         # Create the uploads directory if it doesn't exist
#         uploads_dir = 'uploads'
#         if not os.path.exists(uploads_dir):
#             os.makedirs(uploads_dir)

#         # Generate a filename with a datetime stamp
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"{timestamp}_{file.filename}"
#         filepath = os.path.join(uploads_dir, filename)

#         # Save the file locally
#         file.save(filepath)

#         image_stream = io.BytesIO(file.read())
#         upload_count += 1
        
#         # # Check the content of the result
#         # if "plastic" in result.lower():
#         #     response = "plastic bottle"
#         # elif "glass" in result.lower():
#         #     response = "glass bottle"
#         # else:
#         #     response = "not found"

#         response = "image saved"
        
#         return response, 200  # Return plain text with a 200 status code
    
#     return "No image uploaded", 400  # Return plain text error message


@app.route('/latestimage', methods=['GET'])
def latest_image_route():
    if latest_image is None:
        return "No image uploaded yet", 404
    
    # Reset the stream position to the beginning
    latest_image.seek(0)
    
    # Use PIL to get the image dimensions and size
    image = Image.open(latest_image)
    width, height = image.size
    size = latest_image.getbuffer().nbytes  # Size in bytes
    
    # Reset the stream position to serve the image
    latest_image.seek(0)
    
    # Serve the image
    return send_file(latest_image, mimetype='image/jpeg')

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

@app.route('/sendsms', methods=['POST'])
def send_sms():
    # Retrieve the "to" and "text" fields from the request body
    to = request.json.get('to')
    text = request.json.get('text')

    if not to or not text:
        return jsonify({'error': 'Both "to" and "text" are required fields'}), 400

    # Get the "Authorization" header from environment variables
    authorization = os.getenv('INFOBIP_AUTH')
    if not authorization:
        return jsonify({'error': 'Authorization token not found in environment variables'}), 500

    # Set the "from" field to the hardcoded value
    from_number = '447491163443'

    # Prepare the payload for the Infobip API request
    payload = json.dumps({
        "messages": [
            {
                "destinations": [{"to": to}],
                "from": from_number,
                "text": text
            }
        ]
    })

    # Prepare the headers for the Infobip API request
    headers = {
        'Authorization': f'App {authorization}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Make the API request to Infobip
    try:
        conn = http.client.HTTPSConnection("api.infobip.com")
        conn.request("POST", "/sms/2/text/advanced", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # Return the response from Infobip
        return jsonify({'response': json.loads(data.decode("utf-8"))}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/sendtext2telegram', methods=['POST'])
def send_text_to_telegram():
    # Get the Telegram API token from the environment variable
    api_token = os.getenv('TELEGRAM_API_KEY1')
    if not api_token:
        return jsonify({'error': 'Telegram API token not found in environment variables'}), 500

    # Retrieve the message and chatID from the request body
    tmessage = request.json.get('tmessage')
    chat_id = request.json.get('chatID')

    if not tmessage or not chat_id:
        return jsonify({'error': '"tmessage" and "chatID" are required fields'}), 400

    # Prepare the URL for sending the message
    message_api_url = f'https://api.telegram.org/bot{api_token}/sendMessage'

    try:
        # Send the message via Telegram API
        response = requests.post(message_api_url, json={'chat_id': chat_id, 'text': tmessage})
        
        # Check if the request was successful
        if response.status_code == 200:
            return "ok", 200  # Return "ok" if successful
        else:
            return jsonify({'error': 'Failed to send message', 'details': response.json()}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Server is running"



if __name__ == '__main__':
    app.run(debug=True)
