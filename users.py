"""
Module to handle /messages API calls.
"""

import asyncio
import uuid

from jsonschema import validate


class UsersNewAPI:
    """ Main /packages API class."""

    def __init__(self, db):
        self.db = db
        self.json_schema = {
            "userID": "userID",
            "publicKeyEnc": "pubkeyencryption",
            "publicKeySig": "publicKeySig",
        }

    async def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        validate(data, self.json_schema)



        userID = data.get("userID")
        if userID is None:
            raise ValueError('"userID" attribute is missing')

        publicKeyEnc = data.get("publicKeyEnc")
        if publicKeyEnc is None:
            raise ValueError('"publicKeyEnc" attribute is missing')

        publicKeySig = data.get("publicKeySig")
        if publicKeySig is None:
            raise ValueError('"publicKeySig" attribute is missing')

        # message_id = str(uuid.uuid4())

        response = await self.db.insertUser(userID, publicKeyEnc, publicKeySig)

        # response = {
        #     'message_id': message_id,
        #     'message': message
        # }

        return response
