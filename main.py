from __future__ import division
from spotify import spot

import argparse, re, sys, os, pyaudio, webbrowser

from google.cloud import language
from google.cloud.language import enums as lang_enums
from google.cloud.language import types as lang_types

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from six.moves import queue

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


#built off of gcloud's quickstart method, listens until pause
def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript

        if result.is_final:
            sys.stdout.flush()
            #printing and returning user's statement
            print('Creating playlist from: ' + transcript[0:len(transcript)] + "\n")
            return(transcript)
            break

#passing in user's statement, running against gcloud's sentiment analysis, then normalizing scale from 0-1 and returning
#method also calls method that generates playlist from spotify.py file
def sentiment(string):
    language_code = 'en-US'
    client = language.LanguageServiceClient()
    string = string[0:len(string)]
    data = lang_types.Document(content=string,type=lang_enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=data).document_sentiment
    score = round(sentiment.score,2)
    valience = (score+1)/2
    return(spot(valience))
    
def main():
    os.system('clear')
    print("""\
==================================================================================

                     /$$$$$$$  /$$                     /$$ /$$             /$$    
                    | $$__  $$| $$                    | $$|__/            | $$    
  /$$$$$$  /$$$$$$$$| $$  \ $$| $$  /$$$$$$  /$$   /$$| $$ /$$  /$$$$$$$ /$$$$$$  
 /$$__  $$|____ /$$/| $$$$$$$/| $$ |____  $$| $$  | $$| $$| $$ /$$_____/|_  $$_/  
| $$$$$$$$   /$$$$/ | $$____/ | $$  /$$$$$$$| $$  | $$| $$| $$|  $$$$$$   | $$    
| $$_____/  /$$__/  | $$      | $$ /$$__  $$| $$  | $$| $$| $$ \____  $$  | $$ /$$
|  $$$$$$$ /$$$$$$$$| $$      | $$|  $$$$$$$|  $$$$$$$| $$| $$ /$$$$$$$/  |  $$$$/
 \_______/|________/|__/      |__/ \_______/ \____  $$|__/|__/|_______/    \___/  
                                             /$$  | $$                            
                                            |  $$$$$$/                            
                                             \______/
==================================================================================

Tell me how you're feeling and I will do the the rest! - Make sure not to pause for too long, or I will think you are done!

    """)
    
    language_code = 'en-US'

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        #grabbing user's statement, and then passing into sentiment analysis
        statement = listen_print_loop(responses)
        #creating url from playlist id and opening in user's default web browser
        url = "https://open.spotify.com/playlist/" + str(sentiment(statement))
        webbrowser.open(url, new=0, autoraise = True)

if __name__ == '__main__':
    main()
