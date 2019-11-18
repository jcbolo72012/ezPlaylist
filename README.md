# ezPlaylist
BostonHacks 2019 - Playlist Creation Tool: Experience music in a new light, experience music from ezPlaylist

ezPlaylist records audio from the user and then uses Google's Speech to Text API to convert the audio to text. We then use Google's Sentiment API and Spotify's API to match songs to the audio and create a playlist.

Project by Patrick Kuzdzal, Conor Walsh, Justin Sayah, and John Bolognino


# Instructions
- Navigate to your project on the Google Cloud website, enable the Speech to Text and Sentiment Analysis APIs.

- While on the Cloud website, generate your service usage keys, then run the command ' export GOOGLE_APPLICATION_CREDENTIALS="[PATH]" '

- Install the required modules, running ' pip install requirements.txt '

- Run the project by navigating to the ezPlaylist directory on your machine in your terminal and then typing ' python3 main.py '

- Once running, talk until you deem fit, and upon pausing, our program will turn your statement into a customized/randomized Spotify playlist for you to enjoy
