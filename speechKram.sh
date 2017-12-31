#!/bin/bash
#script to start the needed programs in the right order
#is located under /usr/local/bin
#script umd die benoetigten Programme tatsaechlich nacheinander zu starten
#liegt bei mir in /usr/local/bin
#evtl. genutzte Ports frei geben /"free" ports
fuser -k 3000/tcp
fuser -k 5123/tcp
#probleme mit dem starten - kommt avs zu früh, startet er, läuft aber nicht
#scheint auch auf port 5123 connection anzubieten
#authorisierungsserver fuer alexa starten
cd /home/pi/alexa-avs-sample-app/samples/companionService && npm start > /tmp/npm.out &
found=0
while [ $found -eq 0 ]
do
   sleep 1
   cat /tmp/npm.out | grep "Listening on port"
   found=$((1-$?)) #toggle
   echo "Listening found, npm started: $found"
done   
#java programm avs starten, warte bis es da ist
cd /home/pi/alexa-avs-sample-app/samples/javaclient && mvn exec:exec > /tmp/javaclient.out&  
found=0
while [ $found -eq 0 ]
do
   sleep 1
   cat /tmp/javaclient.out | grep "Display this help text again" 
   found=$((1-$?)) #toggle
   echo "Messages found, javaclient started: $found"
done   

#und mein Programm starten 
/home/pi/snowAlexaGoogle/snowAlexaGoogle.sh

