import os
import openai
from datetime import datetime
from pyfiglet import Figlet

# Ottieni il percorso assoluto del file corrente
current_file_path = os.path.abspath(__file__)

# Ottieni il percorso della cartella che contiene il file corrente
current_dir = os.path.dirname(current_file_path)

# Ottieni il nome della cartella
current_dir_name = os.path.basename(current_dir)

# Configura la tua chiave API di OpenAI
openai.api_key = 'your_openai_APi_key'

def trova_ultimo_file(cartella):
    files = [os.path.join(cartella, f) for f in os.listdir(cartella) if os.path.isfile(os.path.join(cartella, f))]
    if not files:
        return None
    ultimo_file = max(files, key=os.path.getctime)
    return ultimo_file

def leggi_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        contenuto = file.read()
    return contenuto

def fai_riassunto(testo):
    response = openai.ChatCompletion.create(
        # model="gpt-4o",
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Setup_here_your_system_prompt"},
            {"role": "user", "content": f" Setup_here_your_user_prompt \n\n{testo}"}
        ],
        max_tokens=4096,
        temperature=0.7,
    )
    riassunto = response['choices'][0]['message']['content'].strip()
    return riassunto

def salva_riassunto(file_name, riassunto):
    if not os.path.exists('summarized'):
        os.makedirs('summarized')
    file_path = os.path.join('summarized', file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(riassunto)

def main():
    cartella_transcripts = 'transcripts'
    ultimo_file = trova_ultimo_file(cartella_transcripts)
    if ultimo_file:
        print(f"Trovato ultimo file: {ultimo_file}")
        contenuto = leggi_file(ultimo_file)
        riassunto = fai_riassunto(contenuto)
        file_name = f"summarized_{os.path.basename(ultimo_file)}"
        salva_riassunto(file_name, riassunto)
        print(f"Riassunto salvato in: summarized/{file_name}")
    else:
        print("Nessun file trovato nella cartella transcripts.")
    
    f = Figlet(font='slant')
    print(f.renderText(current_dir_name))
    print(current_dir_name)
    print(riassunto)

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Ottieni il percorso della directory in cui si trova lo script
    percorso_script = os.path.dirname(os.path.abspath(__file__))
    
    # Ottieni il percorso della directory superiore
    percorso_superiore = os.path.dirname(percorso_script)
    
    # Crea il percorso completo della cartella Summary nella directory superiore
    summary_dir = os.path.join(percorso_superiore, "Summary")
    
    # Crea la cartella Summary se non esiste
    if not os.path.exists(summary_dir):
        os.makedirs(summary_dir)
        print(f"Cartella 'Summary' creata in: {summary_dir}")
    else:
        print(f"Cartella 'Summary' esiste già in: {summary_dir}")
    
    # Nome del file di output
    output_file = os.path.join(summary_dir, f"{current_date}.txt")

    # Scrivi il contenuto nel file
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(f.renderText(current_dir_name))
        file.write(current_dir_name)
        file.write(riassunto)

if __name__ == "__main__":
    main()
