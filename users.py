"""
Module to handle /messages API calls.
"""

from jsonschema import validate


class UsersAPI:
    """ Main /packages API class."""

    def __init__(self, db):
        self.my_db = db

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        json_schema = {
            "type": "object",
            "properties": {
                "public_key": {"type": "string"},
            },
            "required": ["public_key"]
        }

        validate(data, json_schema)

        public_key_sig = data.get("public_key_sig")



        await self.my_db.insert_user(user_id, public_key_enc, public_key_sig)

        response = {
            'user_id': user_id,
            'public_key_enc': public_key_enc,
            'public_key_sig': public_key_sig
        }

        return response

    async def process_get(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        json_schema = {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
            },
            "required": ["user_id"]
        }

        validate(data, json_schema)

        user_id = data.get("user_id")

        api_response = await self.my_db.select_user(user_id)

        assert isinstance(api_response, list)
        if len(api_response) > 1:
            raise NotImplementedError
        api_response = api_response[0]

        public_key_enc = api_response.get("public_key_enc")
        public_key_sig = api_response.get("public_key_sig")

        response = {
            'user_id': user_id,
            'public_key_enc': public_key_enc,
            'public_key_sig': public_key_sig
        }

        return response
