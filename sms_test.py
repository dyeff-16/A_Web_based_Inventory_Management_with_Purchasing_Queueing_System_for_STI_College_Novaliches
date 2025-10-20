import requests

API_TOKEN = '4fcbae81935679f94bf6179b6a1d3114aabb2825'
phone_number = '09666412225'
message = 'Your One Time Password in Stiprowarenovaliches: 123456' 

url = 'https://sms.iprogtech.com/api/v1/sms_messages'

payload = {
    "api_token"   : API_TOKEN,
    "phone_number": phone_number,
    "message"     : message
}

resp = requests.post(url, json=payload)
print("Response JSON:", resp.json())