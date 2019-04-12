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
