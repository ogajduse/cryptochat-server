"""
Module to handle /messages API calls.
"""

from jsonschema import validate


class MessagesNewAPI:
    """ Main /messages/new API class."""

    def __init__(self, my_db):
        self.my_db = my_db
        self.json_schema = {
            'type': 'object',
            'properties': {
                'chat_id': {'type': 'integer'},
                'sender_id': {'type': 'integer'},
                'message': {'type': 'string'},
            },
            'required': ['chat_id', 'sender_id', 'message']
        }

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process inserting new message to the chat.
        :param data: json request parsed into data structure
        :returns: json response with inserted message
        """
        validate(data, self.json_schema)

        message = data.get('message')
        chat_id = data.get('chat_id')
        sender_id = data.get('sender_id')

        await self.my_db.insert_message(chat_id, sender_id, message)

        response = {
            'chat_id': chat_id,
            'sender_id': sender_id,
            'message': message
        }

        return response


class MessagesUpdatesAPI:
    """ Main /messages/updates API class."""

    def __init__(self, my_db):
        self.my_db = my_db
        self.json_schema = {
            "cursor": "uuid"
        }
        self.wait_future = None

    async def process_post(self, api_version, data):  # pylint: disable=unused-argument
        """
        Process the request for new messages since the cursor.
        :param data: json request parsed into data structure
        :returns: json response with a list of messages
        """
        validate(data, self.json_schema)

        cursor = data.get("cursor")
        if cursor is None:
            raise ValueError('"cursor" attribute is missing')

        # messages = self.cache.get_messages_since(cursor)
        # while not messages:
        #     # Save the Future returned here so we can cancel it in
        #     # on_connection_close.
        #     self.wait_future = self.cache.cond.wait()
        #     try:
        #         await self.wait_future
        #     except asyncio.CancelledError:
        #         return
        #     messages = self.cache.get_messages_since(cursor)

        response = {
            'messages': None
        }

        return response
