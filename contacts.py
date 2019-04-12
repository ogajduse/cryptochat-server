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
