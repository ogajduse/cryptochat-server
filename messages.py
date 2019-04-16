"""
Module to handle /messages API calls.
"""

import hashlib

from jsonschema import validate
from rsa.key import PublicKey as rsa_public_key
from rsa.transform import int2bytes

from utils import rsa_decryption


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
                'hash': {'type': 'integer'}
            },
            'required': ['chat_id', 'sender_id', 'message', 'hash']
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

        received_hash_signed = int2bytes(received_hash_signed)

        response = await self.my_db.select_user(sender_id)
        user_public_key = response['public_key']
        user_public_key = rsa_public_key.load_pkcs1(user_public_key)

        generated_hash = hashlib.sha256((str(chat_id) + str(sender_id) + str(message)).encode()).hexdigest()

        decrypted_hash = rsa_decryption(user_public_key, received_hash_signed)  # falling here

        timestamp = await self.my_db.insert_message(chat_id, sender_id, message)

        if decrypted_hash == generated_hash:
            await self.my_db.insert_message(chat_id, sender_id, message)
        # else:
        # TODO: GET ERROR !!!!!! SEND INFO TO CLIENT WARNING ABOUT BAD SIGN

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
