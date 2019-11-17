from __future__ import division
from spotify import spot

import argparse

from google.cloud import language
from google.cloud.language import enums as lang_enums
from google.cloud.language import types as lang_types

import re
import sys
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
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


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript

        overwrite_chars = '' * (num_chars_printed - len(transcript))

        if not result.is_final:
            #sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            #print(transcript + overwrite_chars)

            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Creating playlist from: ' + transcript[0:len(transcript)-5])
                return(transcript)
                break

            num_chars_printed = 0

def sentiment(string):
    language_code = 'en-US'
    client = language.LanguageServiceClient()
    string = string[0:len(string)-5]
    data = lang_types.Document(content=string,type=lang_enums.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(document=data).document_sentiment
    score = round(sentiment.score,2)
    valience = (score+1)/2
    return(spot(valience))
    
def main():
    os.system('clear')
    print("""\


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

        x = listen_print_loop(responses)
        y = sentiment(x)
        print("Your playlist: https://open.spotify.com/playlist/"+str(y)+'\n')
        

if __name__ == '__main__':
    main()
