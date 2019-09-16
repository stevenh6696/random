import json
import string
from wordcloud import WordCloud

# https://apps.timwhitlock.info/emoji/tables/unicode
emojiNames = {
    '\u00f0\u009f\u0091\u008e': 'thumbs_down',
    '\u00f0\u009f\u0098\u00a0': 'angry',
    '\u00f0\u009f\u0098\u008d': 'heart',
    '\u00f0\u009f\u0091\u008d': 'thumbs_up',
    '\u00f0\u009f\u0098\u0086': 'funny',
    '\u00f0\u009f\u0098\u00a2': 'cry',
    '\u00f0\u009f\u0098\u00ae': 'surprise',
    '\u00e2\u009d\u00a4': 'heart'
}


# Open file and return as JSON
def get_msgs():
    with open('./message.json') as jsonFile:
        return json.load(jsonFile)


msgs = get_msgs()

# Print participant names
names = list(map(lambda x: x['name'], msgs['participants']))
print("Participants:", ", ".join(names))

# Set up dicts
responseTimes = dict((name, []) for name in names)
numMsgs = dict((name, 0) for name in names)
msgLengths = dict((name, []) for name in names)
msgText = dict((name, '') for name in names)
reacts = dict((name, {}) for name in names)
for name in reacts.keys():
    reacts[name] = dict((emojiNames[emoji], 0) for emoji in emojiNames.keys())

# Keep track of last send
lastSender = msgs['messages'][0]['sender_name']
lastTime = msgs['messages'][0]['timestamp_ms']

# Parse all messages
for msg in reversed(msgs['messages']):

    sender = msg['sender_name']
    text = msg.get('content', '')
    time = msg['timestamp_ms']

    # Record for number of messages
    numMsgs[sender] += 1

    # Record message length
    length = len(text.split())
    msgLengths[sender].append(length)

    # Record reacts
    reactions = msg.get('reactions', [])
    for reaction in reactions:
        actor = reaction['actor']
        emoji = emojiNames[reaction['reaction']]
        reacts[actor][emoji] += 1

    # Record response times
    if lastSender != sender:
        responseTimes[sender].append(time - lastTime)
    lastSender = sender
    lastTime = time

    # Record message text without punctuation
    msgText[sender] += text.translate(str.maketrans('', '', string.punctuation))

# Calculate average length
avgMsgLength = {}
for name in msgLengths:
    avgMsgLength[name] = sum(msgLengths[name])/len(msgLengths[name])

# Calculate average time
avgResponseTime = {}
for name in responseTimes:
    avgResponseTime[name] = sum(responseTimes[name])/len(responseTimes[name])

print(numMsgs)
print(avgMsgLength)
for name in reacts.keys():
    print(name)
    print(reacts[name])
print(avgResponseTime)

for name in msgText:
    wordcloud = WordCloud().generate(msgText[name])
    image = wordcloud.to_image()
    image.save(name + '.jpg')

# https://github.com/amueller/word_cloud/blob/master/examples/simple.py