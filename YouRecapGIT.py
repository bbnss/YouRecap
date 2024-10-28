import os
import time
import sys
import yt_dlp
import openai
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable
from config import *
from datetime import datetime
import json
from github import Github
from twitter_poster import generate_and_post_tweet

print("Data e ora locale:", datetime.now())

def show_spinner():
    spinner = "|/-\\"
    for _ in range(20):
        for char in spinner:
            sys.stdout.write(f"\rCaricamento in corso {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\rCaricamento completato! Aspetta.... \n")

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
                    title = entry.get('title', 'Titolo non disponibile')
                    video_info.append({
                        'id': video_id,
                        'upload_date': upload_date,
                        'title': title
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

    return bool(new_ids)

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
    except (TranscriptsDisabled, NoTranscriptAvailable, Exception) as e:
        print(f"Errore trascrizione per il video {video_id}: {str(e)}")
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

def get_next_post_number():
    counter_file = 'post_counter.txt'
    try:
        with open(counter_file, 'r') as f:
            counter = int(f.read().strip())
    except FileNotFoundError:
        counter = 0
    
    counter += 1
    
    with open(counter_file, 'w') as f:
        f.write(str(counter))
    
    return counter

def carica_su_github(riassunti, data_odierna):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    posts_json_path = 'posts.json'
    
    try:
        posts_file = repo.get_contents(posts_json_path)
        posts_data = json.loads(posts_file.decoded_content.decode())
    except:
        posts_data = []

    for nome_canale, info in riassunti.items():
        post_number = get_next_post_number()
        filename = f"post{post_number}.md"
        content = f"""---
author: YouRecap
date: {data_odierna}
fonte: {nome_canale}
titolo: {info['title']}
---

{info['summary']}
"""

        try:
            repo.create_file(f"posts/{filename}", f"Add {filename}", content, branch="main")
            print(f"File {filename} caricato su GitHub con successo.")
        except Exception as e:
            print(f"Errore durante il caricamento del file {filename}: {e}")

        posts_data.append({
            "filename": filename,
            "source": nome_canale,
            "date": data_odierna,
            "title": info['title']
        })

    try:
        repo.update_file(posts_json_path, "Update posts.json", json.dumps(posts_data, indent=2), posts_file.sha, branch="main")
        print("File posts.json aggiornato su GitHub con successo.")
    except Exception as e:
        print(f"Errore durante l'aggiornamento di posts.json: {e}")

def main():
    print("""
__   __          ____                       ____ ___ _____ 
\ \ / /__  _   _|  _ \ ___  ___ __ _ _ __  / ___|_ _|_   _|x   x
 \ V / _ \| | | | |_) / _ \/ __/ _` | '_ \| |  _ | |  | |    x
  | | (_) | |_| |  _ <  __/ (_| (_| | |_) | |_| || |  | |   x x
  |_|\___/ \__,_|_| \_\___|\___\__,_| .__/ \____|___| |_|  x   x
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
        if not video_info:
            print(f"Nessun video trovato per il canale {nome_canale}, passo al prossimo canale.")
            continue

        print(f"Titolo del video più recente: {video_info[0]['title']}")
        
        file_name = os.path.join(cartella_canale, 'video_ids.txt')
        nuovi_video = salva_video_ids(file_name, video_info)
        if not nuovi_video:
            print(f"Nessun nuovo video trovato per il canale {nome_canale}, passo al prossimo canale.")
            continue
            
        cartella_data = os.path.join(cartella_canale, data_odierna)
        if not os.path.exists(cartella_data):
            os.makedirs(cartella_data)

        video_id = video_info[0]['id']
        video_titolo = video_info[0]['title']
        summary_file = os.path.join(cartella_data, f'summary_{video_id}.txt')

        if os.path.exists(summary_file):
            print(f"Il riassunto per il video {video_id} è già stato generato.")
            with open(summary_file, 'r', encoding='utf-8') as f:
                riassunti[nome_canale] = {'summary': f.read(), 'title': video_titolo}
            continue

        transcript, lingua = get_transcript(video_id)
        if not transcript:
            print(f"Impossibile ottenere la trascrizione per {video_id}, passo al prossimo canale.")
            continue

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
            riassunti[nome_canale] = {'summary': summary, 'title': video_info[0]['title']}
        else:
            print(f"Non è stato possibile generare un riassunto per {nome_canale}, passo al prossimo canale.")
            continue

    if riassunti:
        carica_su_github(riassunti, data_odierna)
        generate_and_post_tweet(riassunti)
    else:
        print("Nessun nuovo riassunto da caricare su GitHub o da twittare.")

if __name__ == "__main__":
    main()
