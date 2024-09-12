import tweepy
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

def generate_tweet(riassunti):
    openai.api_key = OPENAI_API_KEY
    
    # Prepara un prompt per OpenAI
    prompt = "SCRIVI IL PROMPT QUI :\n\n"
    for nome_canale, info in riassunti.items():
        prompt += f"- {nome_canale}: {info['summary']}\n"
    prompt += "\nAGGIUNGI QUALCOSA AL PROMPT QUI"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",   #OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "SCRIVI IL PROMPT DI SISTEMA QUI"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=70,
            temperature=0.5
        )
        tweet_text = response.choices[0].message['content'].strip()
        return tweet_text
    except Exception as e:
        print(f"Errore nella generazione del tweet: {e}")
        return None

def post_tweet(tweet_text):
    # Autenticazione con Twitter API v2
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY, 
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN, 
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    try:
        response = client.create_tweet(text=tweet_text)
        print(f"Tweet pubblicato con successo! ID: {response.data['id']}")
    except Exception as e:
        print(f"Errore nella pubblicazione del tweet: {e}")
        print("Salvando il tweet in un file...")
        save_tweet(tweet_text)

def save_tweet(tweet_text):
    try:
        with open('tweet_to_post.txt', 'w', encoding='utf-8') as f:
            f.write(tweet_text)
        print("Tweet salvato nel file 'tweet_to_post.txt'")
        print("Ecco il tweet generato:")
        print("-" * 40)
        print(tweet_text)
        print("-" * 40)
    except Exception as e:
        print(f"Errore nel salvare il tweet: {e}")

def generate_and_post_tweet(riassunti):
    if riassunti:
        tweet_text = generate_tweet(riassunti)
        if tweet_text:
            post_tweet(tweet_text)
    else:
        print("Nessun riassunto disponibile per generare un tweet.")
