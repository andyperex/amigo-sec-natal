import streamlit as st
import base64
import gspread
import random
import os
import json
from google.oauth2.service_account import Credentials

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Function to send emails
# Function to send emails
def send_email(giver, receiver, wish, giver_email):
    try:
        # Email configuration
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASS"]

        # Email content
        subject = "Amigo Secreto 🎁"
        body = f"""
        Olá,

        Você foi sorteado para presentear: {receiver}.
        Desejo de presente: {wish}.

        🎁Feliz Amigo Secreto familia!🎁
        E vamos Gremio pela sul-americana 2025
        """
        # MIME setup
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = giver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Sending email
        server = smtplib.SMTP("smtp.mail.yahoo.com", 587)  # Yahoo SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, giver_email, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email to {giver_email}: {e}")
        return False



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
    background-color: rgba(255, 255, 255, 0.8);
}}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# Google Sheets setup
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_KEY"])
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)

# Authorize and connect to Google Sheets
client = gspread.authorize(credentials)

# Open the Google Sheet by name
SHEET_NAME = "amigoDB"  # Replace with your sheet name
sheet = client.open(SHEET_NAME).sheet1  # Use the first sheet

# Title and description
st.title("Sejam bem-vindos ao melhor Amigo secreto da história mundial.")
st.text("Deixe aqui o seu nome, os 3 desejos e o seu e-mail para saber quem será o seu amigo secreto.")

# Input Form
name = st.text_input("Nombre", placeholder="Escribe tu nombre")
email = st.text_input("Email", placeholder="Escribe tu email")
wishes = st.text_area("Desejos", placeholder="Escribe un mensaje o tus ideas de regalo")

# Submit Button
if st.button("Enviar"):
    if name and email and wishes:
        # Add the participant's data to the Google Sheet
        sheet.append_row([name, email, wishes, "", "No"])
        st.success(f"Obrigado, {name}! Sua inscrição foi registrada.")
    else:
        st.error("Por favor, preencha todos os campos.")

# Fetch all participants from the Google Sheet
rows = sheet.get_all_records()
st.subheader("Participantes Registrados")
for row in rows:
    st.text(f"🎉 {row['name']}")

# Show how many participants are left
num_participants = len(rows)
if num_participants < 6:
    st.warning(f"Ainda faltam {6 - num_participants} participantes para o sorteio.")

# Perform Matching Automatically When 6 Participants Are Registered
# Perform Matching Automatically When 6 Participants Are Registered
if num_participants == 6:
    st.success("O número necessário de participantes foi atingido! Realizando o sorteio...")
    nombres = [row["name"] for row in rows]
    emails = [row["email"] for row in rows]
    wishes = [row["wishes"] for row in rows]

    # Shuffle and match participants
    combined = list(zip(nombres, emails, wishes))  # Combine names, emails, and wishes
    random.shuffle(combined)  # Shuffle combined list to preserve alignment
    nombres, emails, wishes = zip(*combined)  # Unzip back into separate lists

    matches = {}
    for i in range(len(nombres)):
        giver = nombres[i]
        receiver = nombres[(i + 1) % len(nombres)]
        matches[giver] = {
            "receiver": receiver,
            "receiver_wish": wishes[(i + 1) % len(wishes)],  # Assign the correct wish
        }

    # Send Emails
    st.subheader("Enviando e-mails...")
    for i, giver in enumerate(nombres):
        receiver = matches[giver]["receiver"]
        receiver_wish = matches[giver]["receiver_wish"]
        giver_email = emails[i]

        # Skip if email already sent
        if rows[i]["email sent"] == "Yes":
            st.text(f"E-mail já enviado para {giver}.")
            continue

        # Send email and update sheet
        if send_email(giver, receiver, receiver_wish, giver_email):
            sheet.update_cell(i + 2, 5, "Yes")  # Update "email sent" column
            sheet.update_cell(i + 2, 4, receiver)  # Update "receiver" column
            st.text(f"E-mail enviado com sucesso para {giver}!")
        else:
            st.error(f"Erro ao enviar e-mail para {giver}.")

