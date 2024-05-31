import yt_dlp
import os
import shutil

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
                    upload_date = entry.get('upload_date', '00000000')  # Usa una data di default se 'upload_date' non è presente
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

    # Ordina i video per data di pubblicazione (dal più recente al più vecchio)
    sorted_videos = sorted(video_info, key=lambda x: x['upload_date'], reverse=True)

    # Leggi il contenuto esistente del file
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            existing_content = file.read().splitlines()
    else:
        existing_content = []

    # Aggiungi i nuovi ID all'inizio della lista
    new_content = [video['id'] for video in sorted_videos if video['id'] in new_ids] + existing_content

    # Scrivi l'intero contenuto nel file
    with open(file_name, 'w') as file:
        for video_id in new_content:
            file.write(video_id + '\n')

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

def copia_file_nella_cartella(cartella):
    files_da_copiare = ['esegui.sh', 'transcript.py', 'summarize.py']
    for file in files_da_copiare:
        try:
            shutil.copy(file, cartella)
            print(f"Copiato {file} in {cartella}")
        except Exception as e:
            print(f"Errore durante la copia di {file} in {cartella}: {e}")

def main():
    with open('link', 'r') as file:
        channel_urls = file.read().splitlines()

    for channel_url in channel_urls:
        if not channel_url.strip():
            print("URL vuoto trovato, saltando...")
            continue

        nome_canale = estrai_nome_canale(channel_url)
        if nome_canale == 'sconosciuto':
            print(f"Impossibile estrarre il nome del canale per l'URL: {channel_url}")
            continue

        if not os.path.exists(nome_canale):
            os.makedirs(nome_canale)

        video_info = estrai_video_ids(channel_url)
        if video_info:
            file_name = os.path.join(nome_canale, 'video_ids.txt')
            salva_video_ids(file_name, video_info)
            print(f"Salvati {len(video_info)} ID di video nel file {file_name}")
        else:
            print(f"Non sono stati trovati video nel canale {nome_canale}.")

        # Copia i file nella cartella del canale
        copia_file_nella_cartella(nome_canale)

if __name__ == '__main__':
    main()
