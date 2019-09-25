import hashlib
import hmac
import json
import os
import requests
from flask import Flask, request, make_response
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


app = Flask(__name__)


@app.route('/asana-webhook', methods=['POST'])
def asana_webhook():

    # Just in case
    try:
        # Complete creation of new webhook
        if 'X-Hook-Secret' in request.headers:

            # Log new webhook
            secret = request.headers['X-Hook-Secret']
            print('Asana_webhook: webhook added with secret', secret)

            # Record secret
            # Cannot use global variable, so using this for now
            f = open('secrets.txt', 'a+')
            f.write(';%s' % secret)
            f.close()

            # Return secret to complete handshake
            response = make_response('', 200)
            response.headers['X-Hook-Secret'] = secret
            return response

        # Process the new events
        elif 'X-Hook-Signature' in request.headers:

            # Log request
            print('Asana_webhook: new post received:', request.json)

            # Get correct signature to verify request with
            # Example code: https://github.com/Asana/devrel-examples/blob/master/python/webhooks/webhook_inspector.py
            correctSig = request.headers["X-Hook-Signature"]

            # Get secrets of registered webhooks
            f = open('secrets.txt', 'r')
            secrets = f.readline().split(';')
            f.close()

            # Compare signatures
            match = []
            for secret in secrets:
                encoded = secret.encode('ascii', 'ignore')
                sig = hmac.new(encoded, msg=request.data, digestmod=hashlib.sha256).hexdigest()
                match.append(hmac.compare_digest(sig, correctSig))

            # Check if any matched
            if any(match):
                print('Asana_webhook: received digest matches')
            else:
                raise Exception('received digest does not match')

            # Find new events
            for event in request.json.get('events'):

                # Check user, resource type, parent type, and task ID
                user = event.get('user', {}).get('gid') if event.get('user') else None
                resourceSubtype = event.get('resource', {}).get('resource_subtype')
                isTask = event.get('parent').get('resource_type') if event.get('parent') else None
                task = event.get('parent').get('gid') if event.get('parent') else None

                # Check to make sure correct event
                if user != os.environ['ASANA_SELF'] or resourceSubtype != 'added_to_project' \
                        or isTask != 'task':
                    continue

                # Log new task
                print('Asana_webhook: new task found:', task)

                # Set up post request
                url = 'https://app.asana.com/api/1.0/tasks/' + task
                data = {'assignee': 'me'}
                headers = {'Authorization': 'Bearer ' + os.environ['ASANA_TOKEN']}

                # Assign to self
                result = requests.put(url, data=data, headers=headers)

                # Print result
                if result.ok:
                    print('Asana_webhook: new task assigned:', task)
                else:
                    errorMsg = 'failed to assign task: %s %s %s' % (task,
                                                                    result.status_code,
                                                                    result.json())
                    raise Exception(errorMsg)

    # Log all errors
    except Exception as e:
        print('Asana_webhook: error:', e)

    # Return success regardless
    return '', 200


@app.route('/fb-webhook', methods=['GET', 'POST'])
def fb_webhook():

    # Just in case
    try:

        # Complete creation of new webhook
        if request.method == 'GET' and request.args.get('hub.mode') == 'subscribe':

            # Log new webhook
            challenge = request.args.get('hub.challenge')
            print('Fb_webhook: webhook added with challenge', challenge)

            # Return the challenge
            return challenge, 200

        # Process new events
        elif request.method == 'POST' and request.json.get('entry'):

            # Calculate own signature
            encodedSecret = os.getenv('FB_SECRET').encode('ascii', 'ignore')
            encodedMsg = request.data.decode('UTF-8').encode('unicode-escape')
            sig = hmac.new(encodedSecret, msg=encodedMsg, digestmod=hashlib.sha1).hexdigest()

            # Verify with correct signature
            correctSig = request.headers["X-Hub-Signature"][5:]
            if hmac.compare_digest(sig, correctSig):
                print('Fb_webhook: received digest matches')
            else:
                raise Exception('received digest does not match')

            # Process each event
            entries = request.json.get('entry')
            changes = [change for event in entries for change in event.get('changes')]

            # Process each change
            for change in changes:

                # Get event ID, action, and field
                event = change.get('value', {}).get('event_id')
                verb = change.get('value', {}).get('verb')
                field = change.get('field')

                # Confirm expected fields before continuing
                if not event or verb != 'accept' or field != 'events':
                    continue

                # Log new event
                print('Fb_webhook: new event found:', event)

                # Set up get request
                # TODO: refresh token
                url = 'https://graph.facebook.com/v3.3/' + event
                headers = {'Authorization': 'Bearer ' + os.environ['FB_USER']}

                # Query for more information about the event
                result = requests.get(url, headers=headers)

                # Process the query
                if not result.ok:
                    errorMsg = 'event retrieval failed: %s %s %s' % (event,
                                                                     result.status_code,
                                                                     result.json())
                    raise Exception(errorMsg)

                # Log success
                print('Fb_webhook: event logged:', event)

                # Set up credentials
                # Example code: https://github.com/gsuitedevs/python-samples/blob/master/calendar/quickstart/quickstart.py
                bot = json.loads(os.environ['GOOGLE_BOT'])
                creds = Credentials.from_service_account_info(bot)
                service = build('calendar', 'v3', credentials=creds)

                # Convert facebook event info to google calendar format
                eventInfo = result.json()
                event = {
                    'summary': eventInfo.get('name'),
                    'location': eventInfo.get('place', {}).get('name'),
                    'description': eventInfo.get('description'),
                    'start': {
                        'dateTime': eventInfo.get('start_time'),
                    },
                    'end': {
                        'dateTime': eventInfo.get('end_time'),
                    }
                }

                # Creat and log event
                created = service.events().insert(calendarId=os.environ['GOOGLE_CALENDAR'],
                                                  body=event).execute()
                # TODO: check for error here
                print('Fb_webhook: google calendar event created:', created.get('summary'))

    # Log all errors
    except Exception as e:
        print('Fb_webhook: error:', e)

    # Return success regardless
    return '', 200


# Run Flask server
if __name__ == '__main__':
    app.run()
