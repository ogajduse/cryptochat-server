"""
Module to handle /messages API calls.
"""

from jsonschema import validate
import hashlib
from utils import rsa_decryption
import json

class MessagesNewAPI:
    """ Main /messages/new API class."""

    def __init__(self, my_db):
        self.my_db = my_db
        self.json_schema = {
            'type': 'object',
            'properties': {
                'chat_id': {'type': 'integer'},
                'sender_id': {'type': 'integer'},
                'message': {'type': 'string'},
            },
            'required': ['chat_id', 'sender_id', 'message']
        }



    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process inserting new message to the chat.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        validate(data, self.json_schema)

        message = data.get('message')
        chat_id = data.get('chat_id')
        sender_id = data.get('sender_id')
        received_hash_signed = data.get('hash')

        response = await self.my_db.select_user(sender_id)

        response_dumped = json.dumps(response[0])
        response_json = json.loads(response_dumped)

        generated_hash = hashlib.sha256((str(chat_id) + str(sender_id) + str(message)).encode()).digest()

        decrypted_hash = rsa_decryption(response_json['public_key'], received_hash_signed)

        timestamp = await self.my_db.insert_message(chat_id, sender_id, message)

        if decrypted_hash == generated_hash:
            await self.my_db.insert_message(chat_id, sender_id, message)
        #else:
            #TODO: GET ERROR !!!!!! SEND INFO TO CLIENT WARNING ABOUT BAD SIGN

        response = {
            'chat_id': chat_id,
            'sender_id': sender_id,
            'timestamp': timestamp,
            'message': message
        }

        return response


class MessagesUpdatesAPI:
    """ Main /messages/updates API class."""

    def __init__(self, my_db):
        self.my_db = my_db
        self.json_schema = {
            'type': 'object',
            'properties': {
                'cursor': {'type': 'number'},
                'chat_id': {'type': 'integer'}
            },
            'required': ['cursor', 'chat_id']
        }

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the request for new messages since the cursor.
        :param data: json request parsed into data structure
        :returns: json response with a list of messages
        """
        validate(data, self.json_schema)

        cursor = data.get('cursor')
        chat_id = data.get('chat_id')
        db_response = await self.my_db.select_my_messages(chat_id)
        db_response.sort(key=lambda x: x.get('timestamp'), reverse=True)

        results = []
        for msg in db_response:
            if msg['timestamp'] == cursor:
                break
            results.append(msg)
        results.reverse()

        response = {
            'messages': results
        }

        return response
