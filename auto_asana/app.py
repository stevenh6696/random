import json
import os
from flask import Flask, request, make_response

app = Flask(__name__)
secrets = os.environ['SECRETS']
token = os.environ['TOKEN']


@app.route('/asana-webhook', methods=['POST'])
def asana_webhook():

    # Complete creation of new webhook
    if 'X-Hook-Secret' in request.headers:

        # Log new webhook
        print('Asana_webhook: webhook added with secret', request.headers['X-Hook-Secret'])

        # Return secret to complete handshake
        response = make_response('', 200)
        response.headers['X-Hook-Secret'] = request.headers['X-Hook-Secret']
        return response

    # Process the new events
    elif 'X-Hook-Signature' in request.headers and request.headers['X-Hook-Signature'] in secrets:

        # Log request
        print('Asana_webhook: new post received:', request.json)
        return '', 200

    # Error if neither header exists
    else:
        print('Asana_webhook: neither secret nor signature was found')
        raise KeyError


if __name__ == '__main__':
    app.run()
