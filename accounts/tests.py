import requests

TOKEN = "7370433819:AAEGOPlCEVFwq7jG4EaHjeiSw5D2hlQwe5A"
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

response = requests.get(url)
print(response.json())