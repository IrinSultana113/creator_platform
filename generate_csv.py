import requests
import csv

url = "http://127.0.0.1:8000/api/discovery/"
headers = {"Authorization": "Api-Key 46cad9b2128e4d6284814eaf5fc8432c"}

usernames = []
page = 1

while True:
    response = requests.get(url + f"?page={page}", headers=headers)
    data = response.json()

    for item in data["results"]:
        usernames.append(item["username"])


    if not data.get("next"):
        break

    page += 1

with open("creators.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["username"])

    for u in usernames:
        writer.writerow([u])

print("CSV created with", len(usernames), "users")