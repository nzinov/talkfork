import requests
import json
from .tokens import tokens
from .utils import send_comment
from . import utils
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talkfork.settings")

default_thread = '138873'

users = []

for token in tokens:
    utils.oauth2_headers = {'Authorization': 'Bearer ' + token}
    users.append(requests.get("https://api.twistapp.com/api/v2/users/getone", headers=utils.oauth2_headers).json()["id"])

messages = [
    (0, [1], "Hi, where are you?"),
    (4, [], "BIENE"),
    (1, [0], "I've been waiting at A6 for 3 hours!"),
    (5, [], "MORE BIENE"),
    (2, [], "BIENE"),
    (2, [], "Are there any breakfast leftovers?"),
    (3, [], "Dinner will be served soon"),
    (2, [], "Have I missed lunch too?!!"),
    (1, [], "LOL, lunch was at 13")
]

for message in messages:
    utils.oauth2_headers = {'Authorization': 'Bearer ' + tokens[message[0]]}
    recipients = json.dumps([users[el] for el in message[1]])
    send_comment(default_thread, message[2], as_user=True, recipients=recipients)
    input()


