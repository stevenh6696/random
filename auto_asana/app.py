import json
import os
from flask import Flask, request, make_response

app = Flask(__name__)
secrets = []
token = os.environ['TOKEN']
me = os.environ['SELF']


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

            # Check user, action, resource type, task, and parent type
            user = event.get('user', {}).get('gid')
            action = event.get('action')
            resourceType = event.get('resource', {}).get('resource_type')
            task = event.get('resource', {}).get('gid')
            parentType = event.get('parent').get('resource_type') if event.get('parent') else None

            if user == me and action == 'added' and resourceType == 'task' and parentType == 'project':
                print(event)

        return '', 200

    # Error if neither header exists
    else:
        print('Asana_webhook: neither secret nor signature was found')
        raise KeyError


if __name__ == '__main__':
    app.run()
