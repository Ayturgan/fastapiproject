import requests

input = input("enter your email: ")

url = f"https://api.emailhunter.co/v2/email-verifier?email={input}&api_key=51590a7516dd4855a2192a6ed4018e757006cc67"
response = requests.get(url)
data = response.json()
email_verify = data["data"]["status"]

print(email_verify)
