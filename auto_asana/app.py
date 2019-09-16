import os
import requests
from flask import Flask, request, make_response

app = Flask(__name__)
secrets = []


@app.route('/asana-webhook', methods=['POST'])
def asana_webhook():

    # Complete creation of new webhook
    if 'X-Hook-Secret' in request.headers:

        # Log new webhook
        print('Asana_webhook: webhook added with secret', request.headers['X-Hook-Secret'])

        # TODO: keep secrets

        # Return secret to complete handshake
        response = make_response('', 200)
        response.headers['X-Hook-Secret'] = request.headers['X-Hook-Secret']
        return response

    # Process the new events
    elif 'X-Hook-Signature' in request.headers:

        # Log request
        print('Asana_webhook: new post received:', request.json)

        # TODO: verify request

        # Find new events
        for event in request.json.get('events'):

            # Check user, resource type, parent type, and task ID
            user = event.get('user', {}).get('gid')
            resourceSubtype = event.get('resource', {}).get('resource_subtype')
            isTask = event.get('parent').get('resource_type') if event.get('parent') else None
            task = event.get('parent').get('gid') if event.get('parent') else None

            if user == os.environ['ASANA_SELF'] and resourceSubtype == 'added_to_project' \
                    and isTask == 'task':

                # Log new task
                print('Asana_webhook: new task found:', task)

                # Set up post request
                url = 'https://app.asana.com/api/1.0/tasks/' + task
                data = {'assignee': 'me'}
                headers = {'Authorization': 'Bearer ' + os.environ['ASANA_TOKEN']}

                # Assign to self
                result = requests.put(url, data=data, headers=headers)

                # Print result
                # TODO: log error
                if result.ok:
                    print('Asana_webhook: new task assigned:', result.status_code)
                else:
                    print('Asana_webhook: failed to assign task:', task, result.status_code)

        return '', 200

    # Error if neither header exists
    else:
        print('Asana_webhook: neither secret nor signature was found')
        raise KeyError


@app.route('/fb-webhook', methods=['GET', 'POST'])
def fb_webhook():

    # Complete creation of new webhook
    if request.method == 'GET' and request.args.get('hub.mode') == 'subscribe':

        # Log new webhook
        challenge = request.args.get('hub.challenge')
        print('Fb_webhook: webhook added with challenge', challenge)

        # Return the challenge
        return challenge, 200

    # Process new events
    elif request.method == 'POST' and request.json.get('entry'):

        # Process each event
        for event in request.json.get('entry'):

            # Process each change
            for change in event.get('changes'):

                # Get event ID, action, and field
                event = change.get('value', {}).get('event_id')
                verb = change.get('value', {}).get('verb')
                field = change.get('field')

                # Confirm expected fields
                if event and verb == 'accept' and field == 'events':

                    # Log new event
                    print('Fb_webhook: new event found:', event)

                    # Set up get request
                    url = 'https://graph.facebook.com/v3.3/' + event
                    headers = {'Authorization': 'Bearer ' + os.environ['FB_USER']}

                    # Query for more information about the event
                    result = requests.get(url, headers=headers)

                    # Process the query
                    if result.ok:
                        print('Fb_webhook: event logged:', result.json())
                    else:
                        print('Fb_webhook: event failed:', event)

        return '', 200


if __name__ == '__main__':
    app.run()
