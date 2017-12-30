import snowboydecoder
import sys
import signal
import stt_google as stt
from subprocess import run
import shlex
import AmazonIPC as AI

# Demo code for listening to two hotwords at the same time, was the original from snowboy
# modified code to call alexa via the ipc interface of the demo avs service of amazon okHal()
# and the google speech to text service. The result will be passed to xdotool which 
# simulates the keyboard 

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def okHal():
    # snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
    global detector, alexaConnector
    detector.terminate() # stop - we restart if we come back here
    if alexaConnector.connected:
        alexaConnector.sendCommand(AI.IPCommand.WAKE_WORD_DETECTED)
        alexaConnector.receiveUntilDone();
    else:
        print("No connection, try to connect again")
        alexaConnector.connect();
        if alexaConnector.connected:
            alexaConnector.sendCommand(AI.IPCommand.WAKE_WORD_DETECTED)
            alexaConnector.receiveUntilDone();
    return


def inputCalled():
    global detector
    snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
    detector.terminate()
    #time.sleep(0.5)
    result = stt.listen_for_speech(num_phrases=1,autostart=True);
    print ("result of speech recognition is ",result)
    result = result[0]
    if result['confidence'] > 0.3: #start xdotool
        text = result['text'].lower()+""
        if text.startswith("lösch"):
            command = "xdotool key ctrl+a BackSpace"
        else:
            if text.endswith("los") :
                text = text.rsplit(' ',1)[0] + "\n"
            else:
                text += ' '
            command = "xdotool type --delay 100 " + '"'+text+'"'
        args = shlex.split(command)
        run(args);
        #print(args)
    return


# signal abfangen
if len(sys.argv) != 3:
    print("Error: need to specify 2 model names")
    print("Usage: python snowAlexaGoogle.py okHal.pmdl input.pmdl")
    print("first model to call alexa, second to call google speech to text")
    sys.exit(-1)

models = sys.argv[1:]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# functions for handling the tow key-words
# okHal starts alexa (not implemented yet) input calls google speech api and redirect input to x11

# set sensitivity - experimental and start detector
sensitivity = [0.49,0.4]
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
alexaConnector = AI.IPCConnection()
callbacks = [okHal,
             inputCalled]
print('Listening... Press Ctrl+C to exit')
# main loop
# make sure you have the same numbers of callbacks and models
while not interrupted:
    detector.start(detected_callback=callbacks,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
    print("interrupted or action done")
detector.terminate()
