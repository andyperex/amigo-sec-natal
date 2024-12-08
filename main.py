import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import random

# Google Sheets setupa
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = "/Users/cesarperez/Desktop/amigosecreto\\ app/amigo-secreto-111-0ab2a59d84ac.json"
"

# Authorize and connect to Google Sheets
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPE
)
client = gspread.authorize(credentials)

# Open the Google Sheet by name
SHEET_NAME = "amigoDB"  # Replace with your sheet name
sheet = client.open(SHEET_NAME).sheet1  # Use the first sheet


# Get all records from the Google Sheet
nombres = [row["name"] for row in sheet.get_all_records()]  # Replace "name" with the column header for names

# Verifica que hay al menos 6 nombres
if len(nombres) < 6:
    print("O seu email recebera a informacao quando tudos tenham enviado os deseijos")
else:
    # Mezcla los nombres aleatoriamente
    random.shuffle(nombres)

    # Empareja cada persona con la siguiente en la lista
    matches = {}
    for i in range(len(nombres)):
        giver = nombres[i]
        receiver = nombres[(i + 1) % len(nombres)]  # El último se empareja con el primero
        matches[giver] = receiver

    # Imprime los emparejamientos
    for giver, receiver in matches.items():
        print(f"{giver} le regala a {receiver}")
