"""
Module to handle /messages API calls.
"""

from jsonschema import validate


class UsersNewAPI:
    """ Main /packages API class."""

    def __init__(self, db):
        self.my_db = db
        self.json_schema = {
            "user_id": "user_id",
            "public_key_enc": "public_key_enc",
            "public_key_sig": "public_key_sig",
        }

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        validate(data, self.json_schema)

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
