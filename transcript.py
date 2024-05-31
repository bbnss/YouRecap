import os
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable

def ultimo_video(file_path):
    try:
        with open(file_path, 'r') as file:
            ultimo = file.readline().strip()  # Legge la prima riga e rimuove eventuali spazi bianchi
            return ultimo
    except FileNotFoundError:
        print(f"Il file {file_path} non è stato trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return None

def salva_trascrizione(video_id, transcript, lingua):
    # Crea la cartella 'transcripts' se non esiste
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')

    # Nome del file
    file_name = f'transcripts/transcript_{video_id}_{lingua}.txt'

    # Salva la trascrizione nel file
    with open(file_name, 'w', encoding='utf-8') as file:
        for entry in transcript:
            file.write(entry['text'] + '\n')

def main():
    file_path = 'video_ids.txt'
    ultimo = ultimo_video(file_path)
    if ultimo:
        video_id = ultimo

        try:
            # Ottieni tutte le trascrizioni disponibili
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Seleziona la trascrizione nella lingua originale (la prima disponibile)
            transcript = None
            lingua = None
            for t in transcripts:
                if t.is_generated:
                    transcript = t.fetch()
                    lingua = t.language_code
                    break

            if transcript and lingua:
                salva_trascrizione(video_id, transcript, lingua)
                print(f"Trascrizione salvata per il video {video_id} nella lingua originale ({lingua}).")
            else:
                print(f"Nessuna trascrizione trovata per il video {video_id}.")

        except TranscriptsDisabled:
            print(f"Le trascrizioni sono disabilitate per il video {video_id}.")
        except NoTranscriptAvailable:
            print(f"Nessuna trascrizione disponibile per il video {video_id}.")
        except Exception as e:
            print(f"Errore durante l'ottenimento della trascrizione: {e}")

if __name__ == '__main__':
    main()
