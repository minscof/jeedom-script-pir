import sys
import RPi.GPIO as GPIO
from time import time, localtime, strftime, sleep
import urllib2

"""
prerequisite :
python 2.7
sudo pip2 install RPi.GPIO

In jeedom
create virtual equipment with one info command : note the id of this commans
"""

print "Passive infrared sensor starts"

GPIO.setmode(GPIO.BCM)

#GPIO 4 => pin 7 on rpi 2
capteur = 4

# jeedomIP=${4}
if len(sys.argv) > 1:
    jeedomIP = sys.argv[1]
else:
    ''' put IP address of your jeedom key here'''
    jeedomIP = "192.168.0.9"   


if len(sys.argv) > 2:
    jeedomApiKey = sys.argv[2]
else:
    ''' put your key here'''
    jeedomApiKey = "jeedomApiKey for virtual"  
   

# put id of your command here
id = "49905"

#delay between 2 polling
freq_polling = 2

#delay without detection to signal up
delay = 20
    
jeedomCmdOn = "http://" + jeedomIP + "/core/api/jeeApi.php?type=virtual&apikey=" + jeedomApiKey + '&value=1&id='+id
jeedomCmdOff = "http://" + jeedomIP + "/core/api/jeeApi.php?type=virtual&apikey=" + jeedomApiKey + '&value=0&id='+id

last_detection_timestamp = time()
inflight_movement = False

def detection(channel):
    global last_detection_timestamp, inflight_movement, last_start_movement_timestamp 
    last_detection_timestamp = time()
    
    if GPIO.input(capteur) :
        if not inflight_movement :
            inflight_movement = True
            last_start_movement_timestamp = last_detection_timestamp
            urllib2.urlopen(jeedomCmdOn).read()
            print "Movement starts at", strftime("%a, %d %b %Y %H:%M:%S +0000", localtime(last_detection_timestamp))
        else :
            print "...new detection..."
    else :
        print "...detection ends..."    

       
GPIO.setup(capteur, GPIO.IN)

urllib2.urlopen(jeedomCmdOff).read()

GPIO.add_event_detect(capteur, GPIO.BOTH, callback=detection, bouncetime=200) 

print "Passive infrared sensor ready"

try:
    while True:
        if inflight_movement :
            now = time()
            deltat = now - last_detection_timestamp
            if deltat > delay :
                if not  GPIO.input(capteur) :
                    urllib2.urlopen(jeedomCmdOff).read()
                    duration = now - last_start_movement_timestamp
                    print "Movement ends at", strftime("%a, %d %b %Y %H:%M:%S +0000", localtime(time()))
                    print "Duration = ", duration
                    print "Deltat =", deltat
                    inflight_movement = False
        sleep(freq_polling)

  
except KeyboardInterrupt:  
    print "Halt requested"       # clean up GPIO on CTRL+C exit
 
GPIO.cleanup()           # clean up GPIO on normal exit  