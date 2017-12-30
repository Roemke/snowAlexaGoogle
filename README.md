# snowAlexaGoogle
This tool is a small piece of python-software which is used to have a speech input on a Raspberry Pi and  
connect to the Amazon voice service. It is tested only on the Raspberry pi.  
It reacts on two wake words: "ok Hal" and "input". I use the software from snowboy / KittAI
https://github.com/Kitt-AI/snowboy . For the connection to the  
Google speech api I've used code from [jeysonmc/github](https://github.com/jeysonmc/python-google-speech-scripts) 
and adapted this to python3  
 
The wake word "ok Hal" connects to the [Amazon AVS service](https://github.com/alexa/alexa-avs-sample-app) (Alexa / Echo)  
The wakeword  "input" connects to the Google speech api and the spoken words are "typed" by xdotool to the x11-environment.  
I use a pi with touchscreen and by clicking inside an input field I can speak the command input to fill this  
input field. If you say input löschen, the inputfield is cleared. A word followed by "los" will append a  
carriage return.  
Meanwhile the programm is extended to some "buttons". I use it to control a webinterface to realize a click to  
the buttons by the corresponding wake word. 

##Requirements:
* pi with microphone and speaker
* all software which is described in the [amazon sample app](https://github.com/alexa/alexa-avs-sample-app/wiki/Raspberry-Pi)  
to connect to AVS. I don't use the wakeword agent described there because I want to implement two  
possible wake words. The file AmazonIPC.py handles the IPC to the AVS of amazon (java application which must run) 
* For the use of the google speech service (I do not use the cloud service, maybe I have to change later),  
you must be a member of the group [Chromium Dev](https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev)  
Then you have to visit the [google developer console](https://console.cloud.google.com/) and create a new project. 
In this project you have to activate the Speech Api - quote from Google "The Speech API allows developers to access  
Google speech-recognition services. It is only available for development and personal use."   
After activating you have get the api key below the point "Zugangsdate / Anmeldedaten erstellen", sorry I  
don't know how it is named in the english version on the developer console.  
The generate apiKey you have to insert into the file stt_google.py
* You need xdotool, I think it is a package for the pi

##License 
* snowboy uses the apache 2.0 License
* jeysonmc uses the MIT License
* This software is licensed under MIT
 


