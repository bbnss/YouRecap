import os
import time
import sys
import yt_dlp
import openai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable
from config import *
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def show_spinner():
    spinner = "|/-\\"
    for _ in range(20):
        for char in spinner:
            sys.stdout.write(f"\rCaricamento in corso {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\rCaricamento completato! Aspetta....     \n")

def estrai_video_ids(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    video_info = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(channel_url, download=False)
            if 'entries' in info_dict:
                for entry in info_dict['entries']:
                    video_id = entry['id']
                    upload_date = entry.get('upload_date', '00000000')
                    video_info.append({
                        'id': video_id,
                        'upload_date': upload_date
                    })
            else:
                print("Nessun video trovato nel canale.")
        except Exception as e:
            print(f"Errore durante l'estrazione dei video: {e}")

    return video_info

def salva_video_ids(file_name, video_info):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            existing_ids = set(file.read().splitlines())
    else:
        existing_ids = set()

    new_ids = {video['id'] for video in video_info} - existing_ids

    sorted_videos = sorted(video_info, key=lambda x: x['upload_date'], reverse=True)

    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            existing_content = file.read().splitlines()
    else:
        existing_content = []

    new_content = [video['id'] for video in sorted_videos if video['id'] in new_ids] + existing_content

    with open(file_name, 'w') as file:
        for video_id in new_content:
            file.write(video_id + '\n')

    return bool(new_ids)  # Restituisce True se ci sono nuovi video

def estrai_nome_canale(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(channel_url, download=False)
            return info_dict.get('uploader', 'sconosciuto')
        except Exception as e:
            print(f"Errore durante l'estrazione del nome del canale: {e}")
            return 'sconosciuto'

def get_transcript(video_id):
    print(f"Recupero la trascrizione per il video: {video_id}")
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        for t in transcripts:
            if t.is_generated:
                transcript = t.fetch()
                lingua = t.language_code
                return transcript, lingua
        print("Nessuna trascrizione generata automaticamente trovata.")
        return None, None
    except TranscriptsDisabled:
        print(f"Le trascrizioni sono disabilitate per il video {video_id}.")
    except NoTranscriptAvailable:
        print(f"Nessuna trascrizione disponibile per il video {video_id}.")
    except Exception as e:
        print(f"Errore durante l'ottenimento della trascrizione: {e}")
    return None, None

def salva_trascrizione(cartella, video_id, transcript, lingua):
    file_name = os.path.join(cartella, f'transcript_{video_id}_{lingua}.txt')
    with open(file_name, 'w', encoding='utf-8') as file:
        for entry in transcript:
            file.write(entry['text'] + '\n')
    return file_name

def summarize_text(text):
    print("Generazione del riassunto in corso...")
    openai.api_key = OPENAI_API_KEY
    
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{USER_PROMPT}\n\n{text}"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        summary = response.choices[0].message['content']
        print("Riassunto generato con successo.")
        return summary
    except Exception as e:
        print(f"Errore nella generazione del riassunto: {e}")
        return None

def invia_email(riassunti):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    email_sender = EMAIL_SENDER
    email_password = EMAIL_PASSWORD
    email_recipient = EMAIL_RECIPIENT
    subject = f'Riassunti YouTube del {datetime.now().strftime("%Y-%m-%d")}'

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = subject

    body = "Ecco i riassunti dei video YouTube più recenti:\n\n"
    for nome_canale, riassunto in riassunti.items():
        body += f"Canale: {nome_canale}\n"
        body += f"{riassunto}\n\n"
        body += "-" * 40 + "\n\n"

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_recipient, msg.as_string())
        server.quit()
        print('Email inviata con successo!')
    except Exception as e:
        print(f'Errore durante l\'invio dell\'email: {e}')

def main():
    print("""
__   __          ____                      
\ \ / /__  _   _|  _ \ ___  ___ __ _ _ __  
 \ V / _ \| | | | |_) / _ \/ __/ _` | '_ \ 
  | | (_) | |_| |  _ <  __/ (_| (_| | |_) |
  |_|\___/ \__,_|_| \_\___|\___\__,_| .__/ 
                                    |_|    
    """)

    show_spinner()

    canali_dir = os.path.join(os.getcwd(), 'canali')
    if not os.path.exists(canali_dir):
        os.makedirs(canali_dir)

    data_odierna = datetime.now().strftime("%Y-%m-%d")
    riassunti = {}

    for channel_url in YOUTUBE_CHANNELS:
        if not channel_url.strip():
            print("URL vuoto trovato, saltando...")
            continue

        nome_canale = estrai_nome_canale(channel_url)
        if nome_canale == 'sconosciuto':
            print(f"Impossibile estrarre il nome del canale per l'URL: {channel_url}")
            continue

        cartella_canale = os.path.join(canali_dir, nome_canale)
        if not os.path.exists(cartella_canale):
            os.makedirs(cartella_canale)

        video_info = estrai_video_ids(channel_url)
        if video_info:
            file_name = os.path.join(cartella_canale, 'video_ids.txt')
            nuovi_video = salva_video_ids(file_name, video_info)
            if not nuovi_video:
                print(f"Nessun nuovo video trovato per il canale {nome_canale}.")
                continue
            print(f"Salvati {len(video_info)} ID di video nel file {file_name}")
        else:
            print(f"Non sono stati trovati video nel canale {nome_canale}.")
            continue

        cartella_data = os.path.join(cartella_canale, data_odierna)
        if not os.path.exists(cartella_data):
            os.makedirs(cartella_data)

        video_id = video_info[0]['id']
        summary_file = os.path.join(cartella_data, f'summary_{video_id}.txt')
        
        if os.path.exists(summary_file):
            print(f"Il riassunto per il video {video_id} è già stato generato.")
            with open(summary_file, 'r', encoding='utf-8') as f:
                riassunti[nome_canale] = f.read()
            continue

        transcript, lingua = get_transcript(video_id)
        
        if transcript:
            transcript_file = salva_trascrizione(cartella_data, video_id, transcript, lingua)
            print(f"Trascrizione salvata in: {transcript_file}")
            
            transcript_text = " ".join([entry['text'] for entry in transcript])
            summary = summarize_text(transcript_text)
            
            if summary:
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"\nRiassunto del video più recente di {nome_canale}:")
                print("-" * 40)
                print(summary)
                print("-" * 40)
                print(f"Riassunto salvato in: {summary_file}")
                riassunti[nome_canale] = summary
            else:
                print(f"Non è stato possibile generare un riassunto per {nome_canale}.")
        else:
            print(f"Non è stato possibile recuperare la trascrizione per {nome_canale}.")

    if riassunti:
        invia_email(riassunti)
    else:
        print("Nessun nuovo riassunto da inviare via email.")

if __name__ == "__main__":
    main()
