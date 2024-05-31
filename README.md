               __  __                  ____
               \ \/ /___  __  __      / __ \___  _________ _____ 
                \  / __ \/ / / /_____/ /_/ / _ \/ ___/ __ `/ __ \
                / / /_/ / /_/ /_____/ _, _/  __/ /__/ /_/ / /_/ /
               /_/\____/\__,_/     /_/ |_|\___/\___/\__,_/ .___/ 
                                                        /_/      
        _   ___       _    _           ___
       /_\ |_ _| __ _(_)__| |___ ___  / __|_  _ _ __  _ __  __ _ _ _ _  _ 
      / _ \ | |  \ V / / _` / -_) _ \ \__ \ || | '  \| '  \/ _` | '_| || |
     /_/ \_\___|  \_/|_\__,_\___\___/ |___/\_,_|_|_|_|_|_|_\__,_|_|  \_, |
                                                                     |__/ 

# YouTube Video Summarizer

Summarize YouTube videos in blocks by theme. Create the right prompt based on your topic, and using the OpenAI API you can easily have a summary of the videos every day in your email.

## Description

Given a list of YouTube channels, the script searches for the latest video uploaded for each channel, downloads the transcription, and summarizes the video in the language in which the prompt is written. It prints the summary on the screen and sends a file with all the summaries via email.

## Features

- Searches for the latest video uploaded for each channel.
- Downloads the transcription of the video.
- Summarizes the video in the language of the prompt.
- Prints the summary on the screen.
- Sends a file with all the summaries via email.

## Requirements

- Tested only with GPT-3.5-turbo and GPT-4o models.
- Note that the token limit for GPT-3.5 is 16,385, so if the video is very long, you might encounter an error.
- The GPT-4o model supports up to 128,000 tokens, but the cost increases significantly.
- The script currently selects only the latest video uploaded on the channel, so it is suitable only for channels that add one video per day (e.g., news channels, crypto channels, etc.).
- Tested only on Debian 12 in a virtual environment.

## Installation

1. Clone the repository.

2. Install pip:<br>
   sudo apt install pip

3. Install the virtual environment

  sudo apt-get install python3-venv
  python3 -m venv your_venv_name
  source your_venv_name/bin/activate

4. Install dependencies

  pip install -r requirements.txt

5. Settings for summary summarize.py
  Insert the OpenAI API key
  openai.api_key = 'your_openai_API_key'

  Select the model

  model="gpt-4o",
  model="gpt-3.5-turbo",

  Modify the system and user prompt

  {"role": "system", "content": "Setup_here_your_system_prompt"},
  {"role": "user", "content": f" Setup_here_your_user_prompt \n\n{testo}"}

  Modify (optional)

  max_tokens=4096,
  temperature=0.7,

6. Add the channels whose latest video you want to summarize in the link file
  Each channel on a new line in this format
  https://www.youtube.com/@lexfridman/videos

7. Settings for sending Email (optional)
  Set the fields

  smtp_server = 'smtp.gmail.com'
  smtp_port = 587
  email_sender = 'your_sender_email'
  email_password = 'your_password'
  email_recipient = 'your_email_recipient'
  subject = 'Email subject'
  body = "body text"

8. Add execution permissions
  sudo chmod +x start.sh
  sudo chmod +x esegui.sh

9. Start the script
  ./start



