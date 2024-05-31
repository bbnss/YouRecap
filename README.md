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

3. Install the virtual environment<br>

sudo apt-get install python3-venv<br>
python3 -m venv your_venv_name<br>
source your_venv_name/bin/activate<br>

4. Install dependencies<br>

pip install -r requirements.txt<br>

5. Settings for summary summarize.py<br>
Insert the OpenAI API key<br>
openai.api_key = 'your_openai_API_key'<br>

Select the model<br>

model="gpt-4o",<br>
model="gpt-3.5-turbo",<br>

Modify the system and user prompt<br>

{"role": "system", "content": "Setup_here_your_system_prompt"},<br>
{"role": "user", "content": f" Setup_here_your_user_prompt \n\n{testo}"}<br>

Modify (optional)<br>

max_tokens=4096,<br>
temperature=0.7,<br>

6. Add the channels whose latest video you want to summarize in the link file<br>
Each channel on a new line in this format<br>
https://www.youtube.com/@lexfridman/videos<br>

7. Settings for sending Email (optional)<br>
Set the fields<br>

smtp_server = 'smtp.gmail.com'<br>
smtp_port = 587<br>
email_sender = 'your_sender_email'<br>
email_password = 'your_password'<br>
email_recipient = 'your_email_recipient'<br>
subject = 'Email subject'<br>
body = "body text"<br>

8. Add execution permissions<br>
sudo chmod +x start.sh<br>
sudo chmod +x esegui.sh<br>

9. Start the script<br>
./start<br>



