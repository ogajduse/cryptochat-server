"""
Module to handle /messages API calls.
"""

import asyncio
import uuid

from jsonschema import validate


class MessagesNewAPI:
    """ Main /packages API class."""

    def __init__(self, cache):
        self.cache = cache
        self.json_schema = {
            "message": "message"
        }

    async def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        validate(data, self.json_schema)

        message = data.get("message")
        if message is None:
            raise ValueError('"message" attribute is missing')

        message_id = str(uuid.uuid4())

        response = {
            'message_id': message_id,
            'message': message
        }

        self.cache.add_message(response)

        return response


class MessagesUpdatesAPI:
    """ Main /packages API class."""

    def __init__(self, cache):
        self.cache = cache
        self.json_schema = {
            "cursor": "uuid"
        }

    async def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.
        :param data: json request parsed into data structure
        :returns: json response with a list of messages
        """
        validate(data, self.json_schema)

        cursor = data.get("cursor")
        if cursor is None:
            raise ValueError('"cursor" attribute is missing')

        messages = self.cache.get_messages_since(cursor)
        while not messages:
            # Save the Future returned here so we can cancel it in
            # on_connection_close.
            self.wait_future = self.cache.cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return
            messages = self.cache.get_messages_since(cursor)

        response = {
            'message': None
        }

        return dict(messages=messages)
