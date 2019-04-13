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
            'type': 'object',
            'properties': {
                'owner_id': {'type': 'integer'},
                'user_id': {'type': 'integer'},
                'encrypted_alias': {'type': 'string'},
            },
            'required': ['owner_id', 'user_id', 'encrypted_alias']
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

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the data in request and return info about particular contact.
        :param data: json request parsed into data structure
        :returns: json response with all contacts of the given user
        """
        json_schema = {
            'type': 'object',
            'properties': {
                'owner_id': {'type': 'integer'},
            },
            'required': ['owner_id']
        }

        validate(data, json_schema)

        owner_id = data.get('owner_id')

        api_response = await self.my_db.select_my_contacts(owner_id)

        response = {
            'owner_id': owner_id,
            'contacts': api_response,
        }

        return response
