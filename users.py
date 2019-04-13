"""
Module to handle /users API calls.
"""

from jsonschema import validate


class UsersAPI:
    """ Main /users API class."""

    def __init__(self, db):
        self.my_db = db

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process inserting new user to the database.
        :param data: json request parsed into data structure
        :returns: json response with inserted user
        """
        json_schema = {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'},
                'public_key': {'type': 'string'},
            },
            'required': ['user_id', 'public_key']
        }

        validate(data, json_schema)

        public_key = data.get('public_key')
        user_id = data.get('user_id')

        await self.my_db.insert_user(user_id, public_key)

        response = {
            'user_id': user_id,
            'public_key': public_key,
        }

        return response

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the data in request and return info about particular user.
        :param data: json request parsed into data structure
        :returns: json response with user info
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

        api_response = await self.my_db.select_user(user_id)

        public_key = api_response.get('public_key')

        response = {
            'user_id': user_id,
            'public_key': public_key
        }

        return response
