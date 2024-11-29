import base64
import requests
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
class OpenAIHelper:
    def __init__(self):
        pass
    
    def extract_vin_from_image(self, file_path):
        base64_image = encode_image_to_base64(file_path)
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                                Please analyze the attached image visually and extract the from address and to address along with the vin and vehicle maker. 
                                The from and to fields should be in the format of one line rather than object.
                                Do not include addresses unless the location name is unclear. 
                                If you do include address, include its city.
                                Do not include column headers.
                                Do not include any description or explanation about the image. 
                                If you think the image is not related to VIN, then simply return FALSE. Or present the information as json."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        vin = self.make_openai_request(payload)
        return vin
    
    def extract_vin_from_message(self, message):
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                                Please analyze the message below and extract the from address and to address along with the vin and vehicle maker. 
                                The from and to fields should be in the format of one line rather than object.
                                Do not include addresses unless the location name is unclear. 
                                If you do include address, include its city.
                                Do not include column headers.
                                Do not include any description or explanation about the image. 
                                If you think the message is not related to VIN, then simply return FALSE. Or present the information as json..
                                ------- message---------
                                {message}"""
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        vin = self.make_openai_request(payload)
        return vin
    
    def make_openai_request(self, payload):
        # Set headers for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Make the API request
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        # Check for a successful response
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    