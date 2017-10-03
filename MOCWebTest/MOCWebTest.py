import argparse
import geopy.distance
import json
import requests
import settings
from timeit import default_timer as timer 
#from _ast import Param

token = ''
params = {}

def main():
#MOCWebTest -u 'user_name, -p 'password' -c 'Command' -r 'Resource_ID' -d 'PayLoad'
    global params 
    parser = argparse.ArgumentParser()
    parser.add_argument("-u",
                        "--user",
                         help="email address of user")
    parser.add_argument("-p",
                        "--password",
                        help="user's password")
    parser.add_argument("-c",
                        "--command",
                        help="command to be run",
                        default='logon',
                        choices=['logon',
                                 'gettrack',
                                 'getalltracks',
                                 'plottrack',
                                 'timetest'])                    
    parser.add_argument("-r",
                        "--resourceid",
                        help="id of resource to be processed")
    parser.add_argument("-d",
                         "--payload",
                         help="json payload for inserts and updates")
    parser.add_argument("-e",
                         "--environment",
                         default='LOCALTEST',
                         help="environment to use")
         

    args = parser.parse_args()
    params = vars(args)
    if params['command'] == 'logon':
        logon(params['user'], params['password'], params['environment'])
    elif params['command'] == 'gettrack':
        gettrack()
    elif params['command'] == 'plottrack':
        plottrack()    
    elif params['command'] == 'timetest':
        timetest()
        
         
def logon(user, password, environment):
    global token
    logged_in = False
    url = settings.BASE_URL[environment] + '/v1.0/login'
    payload = {'user_id' : user, 
               'password' : password}
    try:
        r = requests.post(url, data=json.dumps(payload))
    except:
        print('Commuication error')
        return logged_in
    if r.status_code == 200:
        resp = json.loads(r.text)
        token = resp['token']
        logged_in = True
    else:
        print('Failed status', r.status_code)
    return logged_in

def gettrack():
    global params
    if logon(params['user'], params['password'], params['environment']):
        print('4')
        url = settings.BASE_URL[params['environment']] +\
              '/v1.0/tracks/' +\
              params['resourceid']
        headers = {'Authorization' : token}
        try:
            r = requests.get(url,headers=headers)
        except:
            print('Commuication error')
            return
        print('5')
        if r.status_code == 200:
            resp = json.loads(r.text)
        else:
            print('Failed status', r.status_code)
            return
    else:
        print ('Log on failed')
        return         
    print(resp)
    
def plottrack():
    global params
    if logon(params['user'], params['password'], params['environment']):
        url = settings.BASE_URL[params['environment']] +\
              '/v1.0/trackdetails/' +\
              params['resourceid']
        headers = {'Authorization' : token}
        try:
            r = requests.get(url,headers=headers)
        except:
            print('Commuication error')
            return
        if r.status_code == 200:
            resp = json.loads(r.text)
        else:
            print('Failed status', r.status_code)
            return
    else:
        print ('Log on failed')
        return        
    track = resp['track']
    details = resp['details']
    previous = None
    total_distance = 0
    for point in details:
        if previous is None:
            previous = point
        else:
            position_prev = (previous['latitude'], previous['longitude'])
            position_curr = (point['latitude'], point['longitude'])
                
            distance = geopy.distance.vincenty(position_prev, position_curr).mi
            total_distance += distance
            previous = point
            
    print('calculated ', total_distance)        
def timetest():
    global params
    for i in range(10):
        start = timer()
        logon(params['user'], params['password'], params['environment'])
        stop = timer()
        print(stop - start)
        

if __name__ == "__main__":
    main()

