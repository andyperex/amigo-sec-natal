import streamlit as st
import base64
import gspread
import random
import os
import json
from google.oauth2.service_account import Credentials


# Function to load the background image and convert it to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return encoded_image


# Determine the path to the background image dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "background.JPEG")
image_base64 = get_base64_image(image_path)

# CSS for styling the page
page_bg = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{image_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
[data-testid="stSidebar"] {{
    background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent sidebar */
}}

/* Style input boxes */
input[type="text"], textarea {{
    background: white !important;
    color: black !important;
    border: 2px solid #cccccc !important;
    padding: 10px !important;
    font-size: 16px !important;
    border-radius: 5px !important;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
}}

[data-testid="stAppViewContainer"] label {{
    font-size: 20px !important; /* Adjusted font size */
    font-weight: 700 !important;
    color: white !important;
    line-height: 1.2 !important;
}}

label {{
    font-size: 25px !important;
    font-weight: 800 !important;
    color: white !important;
    line-height: 1.2 !important;
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
# Load credentials from Streamlit secrets
service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_KEY"])

credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)

# Authorize and connect to Google Sheets
client = gspread.authorize(credentials)

# Open the Google Sheet by name
SHEET_NAME = "amigoDB"  # Replace with your sheet name
sheet = client.open(SHEET_NAME).sheet1  # Use the first sheet

# Title and description
st.title("O melhor AMIGO SECRETO da história mundial")
st.text("Seja bem-vindo ao melhor amigo secreto.")
st.text("Deixe aqui o seu nome, os 3 desejos e o seu e-mail para saber quem será o seu amigo secreto.")

# Input Form
name = st.text_input("Nombre", placeholder="Escribe tu nombre")
email = st.text_input("Email", placeholder="Escribe tu email")
wishes = st.text_area("Desejos", placeholder="Escribe un mensaje o tus ideas de regalo")

# Submit Button
if st.button("Enviar"):
    if name and email and wishes:
        # Add the participant's data to the Google Sheet
        sheet.append_row([name, email, wishes])
        st.success(f"Obrigado, {name}! Sua inscrição foi registrada.")
    else:
        st.error("Por favor, preencha todos os campos.")

# Fetch all participants from the Google Sheet
rows = sheet.get_all_records()
st.subheader("Participantes Registrados")
for row in rows:
    st.text(f"🎉 {row['name']} ")

# Perform Matching
if len(rows) >= 6 and st.button("Sortear Amigo Secreto"):
    # Fetch the names from the sheet
    nombres = [row["name"] for row in rows]

    # Shuffle and match participants
    random.shuffle(nombres)
    matches = {}
    for i in range(len(nombres)):
        giver = nombres[i]
        receiver = nombres[(i + 1) % len(nombres)]  # Last person gives to the first
        matches[giver] = receiver

    # Display the matches
    st.subheader("Resultados do Sorteio")
    for giver, receiver in matches.items():
        st.text(f"{giver} 🎁 vai dar um presente para {receiver}")

service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
if not service_account_key:
    st.error("Service account key is not set. Make sure to configure `.streamlit/secrets.toml` for local testing.")
    st.stop()

service_account_info = json.loads(service_account_key)
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
