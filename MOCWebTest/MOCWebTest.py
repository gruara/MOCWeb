import argparse
import settings

def main():
#MOCWebTest -u 'user_name, -p 'password' -c 'Command' -r 'Resource_ID' -d 'PayLoad' 
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="email address of user")
    parser.add_argument("-p", "--password", help="user's password")
    parser.add_argument("-c", "--command", help="command to be run",default='logon', choices=['logon','gettrack','getalltracks'], )                    
    parser.add_argument("-r", "--resourceid", help="id of resource to be processed")
    parser.add_argument("-d", "--payload", help="json payload for inserts and updates")     

    args = parser.parse_args()
    params = vars(args)
    print(params)
    if params['command'] == 'logon':
        logon(params['user'], params['password'])

def logon(user, password):
    print(user, password)

if __name__ == "__main__":
    main()

