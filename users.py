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
                "user_id": {"type": "integer"},
                "public_key_enc": {"type": "string"},
                "public_key_sig": {"type": "string"},
            },
            "required": ["user_id"]
        }

        validate(data, json_schema)

        user_id = data.get("user_id")
        if user_id is None:
            raise ValueError('"user_id" attribute is missing')

        public_key_enc = data.get("public_key_enc")
        if public_key_enc is None:
            raise ValueError('"public_key_enc" attribute is missing')

        public_key_sig = data.get("public_key_sig")
        if public_key_sig is None:
            raise ValueError('"public_key_sig" attribute is missing')

        # message_id = str(uuid.uuid4())

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
