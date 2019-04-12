"""
Module to handle /chats API calls.
"""

from jsonschema import validate


class ChatsAPI:
    """
    TODO
    """
    def __init__(self, my_db):
        self.my_db = my_db

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted chat
        """
        json_schema = {
            'chat_id': 'chat_id',
            'owner': 'owner',
            'users': 'users',
            'users_public_keys': 'users_public_keys',
        }

        validate(data, json_schema)

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

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns user details.
        :param data: json request parsed into data structure
        :returns: json response with chat info
        """
        json_schema = {
            "type": "object",
            "properties": {
                "chat_id": {"type": "integer"},
            },
            "required": ["chat_id"]
        }

        validate(data, json_schema)

        chat_id = data.get('chat_id')

        api_response = await self.my_db.select_chat(chat_id)

        assert isinstance(api_response, list)
        if len(api_response) > 1:
            raise NotImplementedError
        api_response = api_response[0]

        owner = api_response.get("owner")
        users = api_response.get("users")
        users_public_key = api_response.get("users_public_key")

        response = {
            'user_id': chat_id,
            'owner': owner,
            'users': users,
            'users_public_key': users_public_key,
        }

        return response
