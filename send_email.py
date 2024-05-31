import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

# Configurazione email
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_sender = 'your_sender_email'
email_password = 'your_password'
email_recipient = 'your_email_recipient'
subject = 'Email Subject'

# Ottieni la data odierna nel formato YYYY-MM-DD
today_date = datetime.now().strftime('%Y-%m-%d')

# Percorso del file
file_path = f'Summary/{today_date}.txt'

# Verifica se il file esiste
if not os.path.exists(file_path):
    print(f'Errore: il file {file_path} non esiste.')
else:
    # Crea il messaggio email
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = subject

    # Corpo dell'email
    body = "Email body"
    msg.attach(MIMEText(body, 'plain'))

    # Aggiungi il file come allegato
    with open(file_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

    # Invia l'email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_recipient, msg.as_string())
        server.quit()
        print('Email inviata con successo!')
    except Exception as e:
        print(f'Errore durante l\'invio dell\'email: {e}')
