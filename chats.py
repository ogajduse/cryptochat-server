"""
Module to handle /chats API calls.
"""

from jsonschema import validate


class ChatsAPI:
    """ Main /chats API class."""

    def __init__(self, my_db):
        self.my_db = my_db

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process inserting new chat to the database.
        :param data: json request parsed into data structure
        :returns: json response with inserted chat
        """
        json_schema = {
            'type': 'object',
            'properties': {
                'users': {'type': 'array',
                          'items': {'type': 'integer'}
                          },
                'sym_key_enc_by_owners_pub_keys': {'type': 'array',
                                                   'items': {'type': 'string'}
                                                   },
            },
            'required': ['users', 'sym_key_enc_by_owners_pub_keys']
        }

        validate(data, json_schema)

        users = data.get('users')
        sym_key_enc_by_owners_pub_keys = data.get('sym_key_enc_by_owners_pub_keys')

        await self.my_db.insert_chat(users, sym_key_enc_by_owners_pub_keys)
        chat_id = await self.my_db.get_last_chat()

        response = {
            'chat_id': chat_id,
            'users': users,
            'sym_key_enc_by_owners_pub_keys': sym_key_enc_by_owners_pub_keys,
        }

        return response

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the data in request and return info about particular chat.
        :param data: json request parsed into data structure
        :returns: json response with chat info
        """
        json_schema = {
            'type': 'object',
            'properties': {
                'chat_id': {'type': 'integer'},
            },
            'required': ['chat_id']
        }

        validate(data, json_schema)

        chat_id = data.get('chat_id')

        db_response = await self.my_db.select_chat(chat_id)

        users = db_response.get('users')
        sym_key_enc_by_owners_pub_keys = db_response.get('sym_key_enc_by_owners_pub_keys')

        response = {
            'chat_id': chat_id,
            'users': users,
            'sym_key_enc_by_owners_pub_keys': sym_key_enc_by_owners_pub_keys,
        }

        return response


class ChatsUserAPI:
    """ Main /chats/user API class."""

    def __init__(self, my_db):
        self.my_db = my_db

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the data in request and return info about particular chat.
        :param data: json request parsed into data structure
        :returns: json response with chat info
        """
        json_schema = {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'},
            },
            'required': ['user_id']
        }

        validate(data, json_schema)

        user_id = data.get('user_id')

        db_response = await self.my_db.select_my_chats(user_id)

        response = {
            'user_id': user_id,
            'chats': db_response,
        }

        return response
