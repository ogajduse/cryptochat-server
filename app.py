#!/usr/bin/env python3
"""
Main chat API module
"""

import json
import os
import traceback

import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web
from jsonschema.exceptions import ValidationError
from tornado.options import define, options

from db import DB
from logging_utils import get_logger, init_logging
from messages import MessagesNewAPI
from messages import MessagesUpdatesAPI
from users import UsersNewAPI

LOGGER = get_logger(__name__)
SERVER_VERSION = os.environ.get('VERSION')

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MessageBuffer():
    """Deprecated function that servers as a message buffer. It should be replaced by DB module."""

    def __init__(self):
        # cond is notified whenever the message cache is updated
        self.cond = tornado.locks.Condition()
        self.cache = []
        self.cache_size = 200

    def get_messages_since(self, cursor):
        """Returns a list of messages newer than the given cursor.

        ``cursor`` should be the ``id`` of the last message received.
        """
        results = []
        for msg in reversed(self.cache):
            if msg["message_id"] == cursor:
                break
            results.append(msg)
        results.reverse()
        return results

    def add_message(self, message):
        """Adds message to the buffer."""
        self.cache.append(message)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]
        self.cond.notify_all()


class BaseHandler(tornado.web.RequestHandler):
    """Base handler setting CORS headers."""

    messages_new_api = None
    messages_updates_api = None
    users_new_api = None

    def data_received(self, chunk):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self):
        """Answer OPTIONS request."""
        self.finish()

    def get_post_data(self):
        """extract input JSON from POST request"""
        json_data = ''

        # check if JSON is passed as a file or as a body of POST request
        if self.request.files:
            json_data = self.request.files['file'][0][
                'body']  # pick up only first file (index 0)
        elif self.request.body:
            json_data = self.request.body

        try:
            data = json.loads(json_data)
        except ValueError:
            data = None
        return data

    async def handle_post(self, api_endpoint, api_version):
        """Takes care of validation of input and execution of POST methods."""
        code = 400
        data = self.get_post_data()
        if data:
            try:
                res = await api_endpoint.process_list(api_version, data)
                code = 200
            except ValidationError as validerr:
                if validerr.absolute_path:
                    res = '%s : %s' % (
                        validerr.absolute_path.pop(), validerr.message)
                else:
                    res = '%s' % validerr.message
                LOGGER.error('ValidationError: %s', res)
            except ValueError as valuerr:
                res = str(valuerr)
                LOGGER.error('ValueError: %s', res)
            except Exception as err:  # pylint: disable=broad-except
                err_id = err.__hash__()
                res = 'Internal server error <%s>:' \
                      'please include this error id in bug report.' % err_id
                code = 500
                LOGGER.exception(res)
                LOGGER.info("Input data for <%s>: %s", err_id, data)
        else:
            res = 'Error: malformed input JSON.'
            LOGGER.error(res)

        # raise tornado.web.HTTPError(status_code=444, reason='error happened')
        self.set_status(code)
        self.write(res)

    def handle_get(self, api_endpoint, api_version, param_name, param):
        """Takes care of validation of input and execution of GET methods."""
        result = api_endpoint.process_list(api_version, {param_name: [param]})
        code = 200

        self.set_status(code)
        self.write(result)

    def write_error(self, status_code, **kwargs):

        self.set_header('Content-Type', 'application/json')
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))


class MainHandler(BaseHandler):
    """Handler for the API root."""
    def get(self):
        """Returns the root endpoint of the API."""
        self.write(
            '{"error": "cryptochat-server main page, '
            'please refer to /api/message/new or /api/message/updates"}')


class MessageNewHandler(BaseHandler):
    """Post a new message to the chat room."""

    async def post(self):
        """
        Add a new message to the server.
        """
        await self.handle_post(self.messages_new_api, 1)


class MessageUpdatesHandler(BaseHandler):
    """Long-polling request for new messages.

    Waits until new messages are available before returning anything.
    """

    async def post(self):
        """Checks for the new message updates, waits until
        new messages are available."""
        await self.handle_post(self.messages_updates_api, 1)

    # def on_connection_close(self):
    #     self.wait_future.cancel()


class UsersNewHandler(BaseHandler):
    """Handler class providing /users POST requests."""
    async def post(self):
        """Adds a new user to the database."""
        await self.handle_post(self.users_new_api, 1)


def main():
    """ The main function. It creates cryptochat application, run everything."""
    init_logging()
    cryptochat_db = DB('/tmp/cryptochat_db.json')

    cryptochat_app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/api/message/new", MessageNewHandler),
            (r"/api/message/updates", MessageUpdatesHandler),
            (r"/api/users/insert", UsersNewHandler),
        ],
        debug=options.debug,
        serve_traceback=False,
    )
    cryptochat_app.listen(options.port)
    LOGGER.info("Starting (version %s).", SERVER_VERSION)

    BaseHandler.messages_new_api = MessagesNewAPI(cryptochat_db)
    BaseHandler.messages_updates_api = MessagesUpdatesAPI(cryptochat_db)
    BaseHandler.users_new_api = UsersNewAPI(cryptochat_db)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    # Making this a non-singleton is left as an exercise for the reader.
    GLOBAL_MESSAGE_BUFFER = MessageBuffer()
    main()
