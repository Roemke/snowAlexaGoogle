import sys
import pyaudio
import wave
import audioop
from collections import deque
import os
import urllib.request
import time
import math
import json
import sys

from credentials import apiKey # apikey of google, maybe you would like to enter the key here:
#apiKey = "your key here"
#this is from jeysonmc but modified to work with the v2 api and python 3

LANG_CODE = 'de-DE'  # Language to use
#GOOGLE_SPEECH_URL = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6' % (LANG_CODE)
GOOGLE_SPEECH_URL = 'https://www.google.com/speech-api/v2/recognize'
FLAC_CONV = 'flac -f'  # We need a WAV to FLAC converter. flac is available
                       # on Linux

# Microphone stream config.
CHUNK = 1024 # 4096 #1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000 #44100 # 16000
#rate und chunk in kombination setzen - rate hoch, chunk hoch
#confidence in der antwort von google steigt nicht merklich, lasse es bei 16000

THRESHOLDSTART = 0 # 2500  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).
                  #changes when using rate 44100 instead of 16000
                  #start directly - I use it after wakeword from snowboy

THRESHOLDSTOP = 5000;

THRESHOLD = THRESHOLDSTART

SILENCE_LIMIT = 2  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 2.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.


def audio_int(num_samples=50):
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """

    #print ("Getting intensity values from mic.")
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    #print(values)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2) #20 % lautesten
    #print (" Finished ")
    #print (" Average audio intensity is ", r)
    stream.close()
    p.terminate()
    return r


def listen_for_speech(threshold=THRESHOLD, num_phrases=-1,maxtime=5,autostart=False):
    """
    Listens to Microphone, extracts phrases from it and sends it to 
    Google's TTS service and returns response. a "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    """
    global THRESHOLD
    print ("* Listening mic. ")
    start =time.time()
    #Open stream
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK # 16000 / 1024 = anzahl der chunks die ich fuer eine sekunde brauche
    needlen = int(SILENCE_LIMIT*rel) # er soll mindestens so viele chungs lesen damit halbwegs sicher
    slid_win = deque(maxlen=needlen)
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=int(PREV_AUDIO * rel))
    started = False
    n = num_phrases
    response = []

    while (num_phrases == -1 or n > 0):
        cur_data = stream.read(CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        #sollte gehen, da maxlen gesetzt ist schiebt er den eintrag an das ende und
        #lässt das erste element fallen
        #print ("Read the data, slid_win contains {} elements".format(len(slid_win)))
        #for x in slid_win:
        #    if x > THRESHOLD: add="             THRESHOLD"
        #    else: add=""
        #    print("We have value for x: {} and threshold {}      {}".format(x,THRESHOLD,add))
        summeThresh = sum([x >= THRESHOLD for x in slid_win])
        maximum = max([x for x in slid_win])
        #print("have len of slid_win " , len(slid_win), ",needlen ",needlen ,", max is ", maximum," and sum thresh ", summeThresh)
        actual = time.time()
        #print("recording time: ",actual - start, " start is ",start, " actual is ", actual)
        maxTimeReached = actual > start + maxtime
        #print ("maxTimeReached: ", maxTimeReached)
        #print("Bedingung: " , started is True and (len (slid_win) >= needlen or actual > start + maxtime))
        maxTimeReached = actual > start + maxtime
        if (summeThresh > 0 or autostart is True) and not maxTimeReached:
            if not started:
                print ("Starting record of phrase")
                started = True
                THRESHOLD = THRESHOLDSTOP
            autostart = False
            audio2send.append(cur_data)
        elif started is True and (len (slid_win) >= needlen or maxTimeReached):
            #print ("Finished")
            # The limit was reached, finish capture and deliver.
            #print ("we have len of prev_audio {}".format(len(prev_audio)))
            #print ("we have len of audio2send {}".format(len(audio2send)))
            filename = save_speech(list(prev_audio) + audio2send, p)
            # Send file to  Google and get response
            r = stt_google_wav(filename)
            if num_phrases == -1: #ausgeben wenn ständig gelauscht wird
                print ("Response {} with confidence {}".format(r['text'],r['confidence']))
            else:
                response.append(r)
            #we have also r['confidence'] but in the moment it is not in use
            # Remove temp file. Comment line to review.
            os.remove(filename)
            # Reset all
            started = False
            slid_win = deque(maxlen=int(SILENCE_LIMIT * rel))
            # Prepend audio from 0.5 seconds before noise was detected
            prev_audio = deque(maxlen=int(PREV_AUDIO * rel))
            audio2send = []
            stream.close()
            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            n -= 1
            #print ("Listening ...")
        else:
            prev_audio.append(cur_data)

    #print ("* Done recording")
    stream.close()
    p.terminate()

    return response


def save_speech(data, p):
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """
    #following shows that data is a list contaning lists of bytes
    # print ("Type of data is {}", type(data))
    # for h in data:
    #     print ("Type of data elements is {}", type(h))
    #     for j in h:
    #        print(" -- Type of data elements is {} and element is {}", type(j),j)
    # print ("len of bytearray is {}",len(bytes))
    bytes = bytearray(); #empty
    for i in data:
        for j in i:
            bytes.append(j);

    filename = '/tmp/output_'+str(int(time.time()))
    # writes data to WAV file
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)  # TODO make this value a function parameter?, just isert RATE
    wf.writeframes(bytes)
    wf.close()
    return filename + '.wav'


def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech 
        service and returns service's response. We need a FLAC 
        converter if audio is not FLAC (check FLAC_CONV). """

    #print ("Sending ", audio_fname)
    #Convert to flac first
    filename = audio_fname
    del_flac = True
    #print ("Converting to flac")
    #print (FLAC_CONV + filename)
    os.system(FLAC_CONV + ' ' + filename)
    filename = filename.split('.')[0] + '.flac'

    #read the flac file
    f = open(filename, 'rb')
    flac_cont = f.read()
    f.close()

    #print ( " we have type {} and len {}".format(type(flac_cont),len(flac_cont)))
    # Headers. A common Chromium (Linux) User-Agent
    hrs = {"User-Agent": "Mozilla/5.0",
           'Content-Type': 'audio/x-flac; rate={}'.format(RATE)}
    #build the data (get)
    data={}
    data['output'] = 'json'
    data['lang'] = LANG_CODE
    data['key'] = apiKey
    urlValues = urllib.parse.urlencode(data);
    #print ("Sending request to Google TTS whith hrs: {}".format(hrs))
    fullUrl = GOOGLE_SPEECH_URL+'?'+urlValues
    #print("Full url is " + fullUrl)
    #print "response", response
    try:
        req = urllib.request.Request(fullUrl,data=flac_cont,headers=hrs)
        with urllib.request.urlopen(req) as p:
            response = p.read()
            #print ("response is {}".format(response))
            response = response.decode('utf-8')
            #print ("response is {}".format(response))
            #seltsames rueckgabeformat z.B.
            # {"result": []}\n
            # {"result": [{"alternative": [{"transcript": "Hallo ich rede mit dir", "confidence": 0.87452459},
            #                              {"transcript": "hallo ich rede mit dir"}], "final": true}], "result_index": 0}
            response = response[response.find('\n')+1:] # slice
            #print ("response is {}".format(response)) # das ist gueltig
            response = json.loads(response)
            res = response['result'][0]['alternative'][0]['transcript']
            confidence = response['result'][0]['alternative'][0]['confidence']

    except:
        #print ("Couldn't parse service response")
        #print (sys.exc_info())
        res = ''
        confidence = 0

    if del_flac:
        os.remove(filename)  # Remove temp file

    return {'text':res, 'confidence':confidence}


if(__name__ == '__main__'):
    result = listen_for_speech(num_phrases=1)  # listen to mic.
    print (result)
    #print("result is {} with confidence {}".format(result[0]['text'],result[0]['confidence']))
    #print stt_google_wav('hello.flac')  # translate audio file
    #audio_int()  # To measure your mic levels
