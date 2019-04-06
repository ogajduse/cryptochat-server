"""
Module to handle /chats API calls.
"""

from jsonschema import validate


class ChatsNewAPI:
    """
    TODO
    """
    def __init__(self, my_db):
        self.my_db = my_db
        self.json_schema = {
            'chat_id': 'chat_id',
            'owner': 'owner',
            'users': 'users',
            'users_public_keys': 'users_public_keys',
        }

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted chat
        """
        validate(data, self.json_schema)

        chat_id = data.get('chat_id')
        if chat_id is None:
            raise ValueError('"chat_id" attribute is missing')

        owner = data.get('owner')
        if owner is None:
            raise ValueError('"owner" attribute is missing')

        users = data.get('users')
        if users is None:
            raise ValueError('"users" attribute is missing')

        users_public_key = data.get('users_public_key')
        if users_public_key is None:
            raise ValueError('"users_public_key" attribute is missing')

        await self.my_db.insert_chat(chat_id, owner, users, users_public_key)

        response = {
            'chat_id': chat_id,
            'owners': owner,
            'users': users,
            'users_public_keys': users_public_key,
        }

        return response
