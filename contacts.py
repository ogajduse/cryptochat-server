"""
Module to handle /contacts API calls.
"""

from jsonschema import validate


class ContactsAPI:
    """ Main /contacts API class."""

    def __init__(self, my_db):
        self.my_db = my_db

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process inserting new contact to the database.
        :param data: json request parsed into data structure
        :returns: json response with inserted contact
        """
        json_schema = {
            'owner_id': 'owner_id',
            'user_id': 'user_id',
            'encrypted_alias': 'alias'
        }

        validate(data, json_schema)

        owner_id = data.get('owner_id')
        user_id = data.get('user_id')
        encrypted_alias = data.get('encrypted_alias')

        await self.my_db.insert_contact(owner_id, user_id, encrypted_alias)

        response = {
            'owner_id': owner_id,
            'user_id': user_id,
            'encrypted_alias': encrypted_alias,
        }

        return response


class ContactsUserGetAPI:
    """ Main /contacts/user API class."""

    def __init__(self, my_db):
        self.my_db = my_db

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns all contacts for the given user.
        :param data: json request parsed into data structure
        :returns: json response with contacts info
        """
        json_schema = {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
            },
            "required": ["user_id"]
        }

        validate(data, json_schema)

        chat_id = data.get('chat_id')

        api_response = await self.my_db.select_my_contacts(chat_id)

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
