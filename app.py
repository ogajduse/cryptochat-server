#!/usr/bin/env python3
"""
Main chat API module
"""

import json
import os
import signal
import traceback

import tornado.escape
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.web
from jsonschema.exceptions import ValidationError

from db import DB, DatabaseError
from logging_utils import get_logger, init_logging
from messages import MessagesNewAPI
from messages import MessagesUpdatesAPI
from users import UsersAPI
from chats import ChatsAPI, ChatsUserAPI
from contacts import ContactsAPI

LOGGER = get_logger(__name__)
SERVER_VERSION = os.getenv('VERSION', 'unknown')
PUBLIC_API_PORT = 8888
DATABASE_LOCATION = os.getenv('DATABASE_LOCATION', '/tmp/cryptochat_db.json')
_SHUTDOWN_TIMEOUT = 3


class BaseHandler(tornado.web.RequestHandler):
    """Base handler setting CORS headers."""

    messages_new_api = None
    messages_updates_api = None
    users_api = None
    chats_api = None
    chats_user_api = None
    contacts_new_api = None

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

    async def handle_request(self, api_endpoint, api_version):
        """Takes care of validation of input and execution of POST and GET methods."""
        code = 400
        data = self.get_post_data()
        request_method = self.request.method.lower()
        if data:
            try:
                # will call process_get or process_post methods for the given API
                res = await getattr(api_endpoint, 'process_' + request_method)(api_version, data)
                code = 200
            except ValidationError as validerr:
                if validerr.absolute_path:
                    res = '%s : %s' % (
                        validerr.absolute_path.pop(), validerr.message)
                else:
                    res = '%s' % validerr.message
                LOGGER.error('ValidationError: %s', res)
                raise tornado.web.HTTPError(reason=res)
            except ValueError as valuerr:
                res = str(valuerr)
                LOGGER.error('ValueError: %s', res)
                raise tornado.web.HTTPError(reason=res)
            except DatabaseError as dberr:
                err_id = dberr.__hash__()
                res = str(dberr.reason)
                LOGGER.error(res)
                LOGGER.info("Input data for <%s>: %s", err_id, data)
                raise dberr
            except Exception as err:  # pylint: disable=broad-except
                err_id = err.__hash__()
                res = 'Internal server error <%s>:' \
                      'please include this error id in bug report.' % err_id
                code = 500
                LOGGER.exception(res)
                LOGGER.info("Input data for <%s>: %s", err_id, data)
                raise tornado.web.HTTPError(reason=res)
        else:
            res = 'Error: malformed input JSON.'
            LOGGER.error(res)
            raise tornado.web.HTTPError(reason=res)

        # raise tornado.web.HTTPError(status_code=444, reason='error happened')
        self.set_status(code)
        self.write(res)

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
        await self.handle_request(self.messages_new_api, 1)


class MessageUpdatesHandler(BaseHandler):
    """Long-polling request for new messages.

    Waits until new messages are available before returning anything.
    """

    async def post(self):
        """Checks for the new message updates, waits until
        new messages are available."""
        await self.handle_request(self.messages_updates_api, 1)

    # def on_connection_close(self):
    #     self.wait_future.cancel()


class UsersHandler(BaseHandler):
    """Handler class providing /users POST requests."""

    async def post(self):
        """Adds a new user to the database."""
        await self.handle_request(self.users_api, 1)

    async def get(self):
        """Returns details of particular user."""
        await self.handle_request(self.users_api, 1)


class ChatsHandler(BaseHandler):
    """Handler providing /chats POST requests"""

    async def post(self):
        """Adds a new chat to the database."""
        await self.handle_request(self.chats_api, 1)

    async def get(self):
        """Returns details of particular chat."""
        await self.handle_request(self.chats_api, 1)


class ChatsUserHandler(BaseHandler):
    """Handler providing /chats/user GET requests"""

    async def get(self):
        """Returns chats for the given user."""
        await self.handle_request(self.chats_user_api, 1)


class ContactsNewHandler(BaseHandler):
    """Handler providing /contacts POST requests"""

    async def post(self):
        """Adds a new contact to the database"""
        await self.handle_request(self.contacts_new_api, 1)

    async def get(self):
        """Returns details of particular contact."""
        await self.handle_request(self.contacts_new_api, 1)


class Application(tornado.web.Application):
    """ main cryptochat application class """

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/api/message/new", MessageNewHandler),
            (r"/api/message/updates", MessageUpdatesHandler),
            (r"/api/users", UsersHandler),
            (r"/api/chats", ChatsHandler),
            (r"/api/chats/user", ChatsUserHandler),
            (r"/api/contacts", ContactsNewHandler),
        ]

        tornado.web.Application.__init__(self, handlers, debug=True, serve_traceback=False)


def main():
    """ The main function. It creates cryptochat application, run everything."""

    async def shutdown():
        server.stop()
        await tornado.gen.sleep(_SHUTDOWN_TIMEOUT)
        tornado.ioloop.IOLoop.current().stop()
        LOGGER.info("Server was successfully shut down.")

    def exit_handler(sig, frame):  # pylint: disable=unused-argument
        def get_sig_name(sig):
            return dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                        if v.startswith('SIG') and not v.startswith('SIG_')).pop(sig)

        LOGGER.warning("Registered %s, shutting down.", get_sig_name(sig))
        tornado.ioloop.IOLoop.instance().add_callback_from_signal(shutdown)

    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    init_logging()
    cryptochat_db = DB(DATABASE_LOCATION)

    cryptochat_app = Application()
    server = tornado.httpserver.HTTPServer(cryptochat_app)
    server.bind(PUBLIC_API_PORT)
    server.start()
    LOGGER.info("Starting cryptochat (version %s).", SERVER_VERSION)

    BaseHandler.messages_new_api = MessagesNewAPI(cryptochat_db)
    BaseHandler.messages_updates_api = MessagesUpdatesAPI(cryptochat_db)
    BaseHandler.users_api = UsersAPI(cryptochat_db)
    BaseHandler.chats_api = ChatsAPI(cryptochat_db)
    BaseHandler.chats_user_api = ChatsUserAPI(cryptochat_db)
    BaseHandler.contacts_new_api = ContactsAPI(cryptochat_db)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
