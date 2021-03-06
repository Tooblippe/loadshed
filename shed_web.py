
"""
Created on Wed Jan 28 15:19:02 2015
sve
@author: tobie
"""

#!/usr/bin/env python
import time
import json
import BulkSMS  #
import threading

from httplib2 import Http
from datetime import datetime
from datetime import timedelta
from time import sleep




def Send_SMS(msg):
    s =  BulkSMS.Server('username','password',address='bulksms.2way.co.za')
    s.send_sms( ['2779xxxxxx'], msg )


def GetLoadsheddingStage():
    """ Return the current Loadshedding Stage
    0 = No load shedding
    1-3 = Stage 1-3
    """
    h = Http()
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://loadshedding.eskom.co.za/',
            'X-Requested-With': 'XMLHttpRequest'
            }

    timestamp=str(int(time.time()*1000))
    resp, content = h.request("http://loadshedding.eskom.co.za/LoadShedding/GetStatus?_="+timestamp, "GET", headers=headers)

    # Eskom responds with a single number
    # 1 = No load shedding
    # 2 = Stage 1
    # 3 = Stage 2
    # 4 = Stage 3
    response = {}
    if int(resp['status']) == 200:
        response['status'] = 'Success'
        response['stage'] = int(content)-1
    else:
        response['status'] = 'Error'
    return response

def GetLoadsheddingSchedule(supplier,suburb,stage):
    """ Retrieve the next Loadshedding based on suburb and loadshedding stage
    Currently only works for Johannesburg City Power
    supplier values:
    1 = Johannesburg City Power
    """
    if supplier == 1:
        h = Http()
        headers = {'Accept': '*/*', 'Referer': 'https://www.citypower.co.za/customers/Pages/Load_Shedding.aspx', 'Content-Type': 'application/json; charset=utf-8'}

        resp, content = h.request("https://www.citypower.co.za/LoadSheddingSchedule.axd?Suburb="+str(suburb)+"&Stage=Stage"+str(stage), "GET", headers=headers)

    response = {}
    if int(resp['status']) == 200:
        response['status'] = 'Success'
        response['events'] = json.loads(content)
    else:
        response['status'] = 'Error'
    return response

def GetNextLoadsheddingEvent(supplier,suburb,stage):
    """ Get the next Loadshedding Event for the supplied suburb
    """
    events = TidyCityPowerEvents(GetLoadsheddingSchedule(supplier,suburb,stage))
    timestamp=int(time.time())
    for event in events:
        if int(event['StartTimestamp']) < timestamp:
            #print "%s < %s" % (event['StartTimestamp'], timestamp,)
            pass
        else:
            return event
    return None

def TidyCityPowerEvents(events):
    """ City Power returns some rubbish in their events
    Lets clean it up to make our lives easier
    """
    TidiedEvents=[]
    if events['status'] == 'Success':
        for event in events['events']:
            tidy={}
            tidy['StartDate'] = datetime.fromtimestamp(int(event['StartDate'][6:-2])/1000)
            tidy['StartTimestamp'] = int(event['StartDate'][6:-2])/1000
            tidy['EndDate'] = datetime.fromtimestamp(int(event['EndDate'][6:-2])/1000)
            tidy['EndTimestamp'] = int(event['EndDate'][6:-2])/1000
            tidy['Title'] = event['Title']
            tidy['SubBlock'] = event['SubBlock']
            tidy['Suburb'] = event['Suburb']
            TidiedEvents.append(tidy)
        return TidiedEvents
    else:
        return None

def print_all_events(suburb='48-8B'):
    all = ""
    td = timedelta(hours=7)
    for stage in range(4):
        for stage_one in TidyCityPowerEvents(GetLoadsheddingSchedule(1,suburb,stage)):
            s =  "Stage %s: - %s to %s" % (stage, stage_one['StartDate']+td, stage_one['EndDate']+td)
            #print s
            all = all + s +'<br>'
    return all
    
    
# You need to find your Suburb from the citypower website.
def get_info_string(suburb, formating = 'SMS' ):
    stage        = GetLoadsheddingStage()['stage']
    
    
    if formating == 'SMS':
        burb = "Bskrn: %s" % (suburb[3:])
        stage_string = "Stage: %s" % (stage)
    if formating == 'HTML':
        burb = "Boskruin loadshedding block : %s" % (suburb[3:])
        stage_string = "Current Stage: %s" % (stage)


    stage_one   = GetNextLoadsheddingEvent(1,suburb,1)
    stage_two   = GetNextLoadsheddingEvent(1,suburb,2)
    stage_three = GetNextLoadsheddingEvent(1,suburb,3)
    td = timedelta(hours=7)
    
    if formating == 'SMS':
        s_temp = "S"
    if formating == 'HTML':
        s_temp = 'Affected times for next stage: '
    
    one =    "%s1-%s to %s" % (s_temp, stage_one['StartDate']+td, stage_one['EndDate']+td)
    two =    "%s2-%s to %s" % (s_temp, stage_two['StartDate']+td, stage_two['EndDate']+td)
    three =  "%s3-%s to %s" % (s_temp, stage_three['StartDate']+td, stage_three['EndDate']+td)

    print burb
    print stage_string
    print one
    print two
    print three
    
    if formating == 'SMS':
        br = '\n'
    if formating == 'HTML':
        br = '</br></br>'
        
    return {'info': burb + br + stage_string + br + one + br + two + br + three, 'stage' : stage }


   
def start(SMS=True,suburb='48-8B'):
    #first round
    timestamp=datetime.now()
    print timestamp
    print "add 7 hours"
    print "====================="
    #suburb='48-8B' #Boskruin
    info = get_info_string(suburb)
    if SMS:
        Send_SMS( info['info'])
    old_stage = info['stage']
    return old_stage


def monitor_status(SMS=True, suburb='48-8B'):
    old_stage = start(SMS, suburb)
    while True:
        print "sleeping"
        sleep( 30 ) # wait a minute
        print "in the loop"
        timestamp=datetime.now()
        print timestamp
        print "add 7 hours"
        print "====================="
        try:
            print '# getting info'
            print '# old stage', old_stage
            info = get_info_string(suburb)
            print '# new stage', info['stage']
    
            if old_stage <> info['stage']:
                old_stage = info['stage']
                if SMS:
                    Send_SMS( info['info'] )
                    print '# SMS sent'
                print 'new stage set to ', old_stage
            else:
                print "# no stage change"
        except:
            print "sommer error, trying again"



#create flask app
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    td = timedelta(hours=7)
    template = open( 'index.html', 'r').read()
    suburb='48-8B' #Boskruin
    #info =  get_info_string(suburb, formating = 'HTML' )['info']
    stage_one   = GetNextLoadsheddingEvent(1,suburb,1)
    stage_two   = GetNextLoadsheddingEvent(1,suburb,2)
    stage_three = GetNextLoadsheddingEvent(1,suburb,3)
    stage        = GetLoadsheddingStage()['stage']
    
    return template.format(  shed_block = suburb,  
                             stage1_start = stage_one['StartDate']+td, 
                             stage1_end   = stage_one['EndDate']+td,
                             stage2_start = stage_two['StartDate']+td, 
                             stage2_end   = stage_two['EndDate']+td,
                             stage3_start = stage_three['StartDate']+td, 
                             stage3_end   = stage_three['EndDate']+td,
                             stage = stage
                        )


if __name__ == '__main__':
    #start the programs
    run_sms_service = False
    run_web_service = True
    
    if run_sms_service:
        print "Starting SMS deamon...'"
        t = threading.Thread(target=monitor_status)
        t.start()
    
    if run_web_service:
        print "Starting Web service..."
        t = threading.Thread(target=app.run(host='0.0.0.0'))
        t.start()

    
