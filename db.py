"""
Module to handle database calls.
"""

import asyncio
import hashlib
import os
import time
from enum import Enum

import rsa
from aiotinydb import AIOTinyDB
from tinydb import Query, where

from database_error import DatabaseError
from logging_utils import get_logger

# TYPES
# 1: users
# 2: chats
# 3: messages
# 4: contacts

LOGGER = get_logger(__name__)


# all selects return strings


def input_validator(public_key, sign, json_data):
    """
    Validation function for DATABASE inputs.
    :param public_key:
    :param sign:
    :param json_data:
    :return: TODO
    """
    digest = hashlib.sha512(json_data.encode('utf8')).hexdigest()
    digest_decrypted = rsa.decrypt(sign, public_key)
    if digest == digest_decrypted:
        return 0
    return 1


def _get_default_db_path():
    project_root = os.path.dirname(os.path.abspath(__file__))
    full_path = project_root + '/.data/db.json'
    return full_path


class DBType(Enum):
    """
    Enum for database record types.
    """
    USERS = 1
    CHATS = 2
    MESSAGES = 3
    CONTACTS = 4


class DB:
    """
    Database class for handling the database queries
    """

    def __init__(self, db_string=_get_default_db_path()):
        self.db_string = db_string
        self.query = Query()
        LOGGER.info('Using database located at %s', db_string)

    async def insert_user(self, user_id, public_key_enc, public_key_sig):
        """
        Insert a new user to database.
        :param user_id:
        :param public_key_enc:
        :param public_key_sig:
        :return: 0 if the user was added, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not my_db.contains((where('type') == DBType.USERS.value) & (where('id') == user_id)):
                my_db.insert({'type': DBType.USERS.value,
                              'id': user_id,
                              'public_key_enc': public_key_enc,
                              'public_key_sig': public_key_sig})
            else:
                raise DatabaseError(reason=
                                    'Can not insert user into the database. '
                                    'User with ID "{}" already exist.'.format(user_id))
            return

    async def select_user(self, user_id):
        """
        Return the user that was searched.
        :param user_id:
        :return: user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search((where('type') == DBType.USERS.value) & (where('id') == user_id))

    async def insert_chat(self, chat_id, owner, users, users_public_keys):
        """
        Inserts the new entry to the particular chat.
        :param chat_id:
        :param owner:
        :param users:
        :param users_public_keys:
        :return: 0 if the chat was inserted into the database, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not my_db.contains((where('type') == DBType.CHATS.value) &
                                  ((where('id') == chat_id) | (where('users').all(users)))):
                my_db.insert({'type': DBType.CHATS.value, 'id': chat_id, 'owner': owner,
                              'users': users, 'users_public_key': users_public_keys})
                return
            raise DatabaseError(reason=
                                'Can not insert chat into the database. '
                                'Chat with ID "{}" already exist.'.format(chat_id))

    async def select_chat(self, chat_id):
        """
        Return the chat ID that was searched for.
        :param chat_id:
        :return: Chat that was searched for
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search((where('type') == DBType.CHATS.value) & (where('id') == chat_id))

    async def select_my_chats(self, my_id):
        """
        Return the chats for the particular user.
        :param my_id:
        :return: Chats for the particular user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search(
                (where('type') == DBType.CHATS.value) & ((where('users').any([my_id])) |
                                                         (where('owner') == my_id)))

    async def insert_message(self, chat_id, sender_id, message):
        """
        Insert a message into the chat.
        :param chat_id:
        :param sender_id:
        :param message:
        :return: TODO
        """
        async with AIOTinyDB(self.db_string) as my_db:
            my_db.insert({'type': DBType.MESSAGES.value,
                          'chat_id': chat_id,
                          'sender_id': sender_id,
                          'timestamp': time.time(),
                          'message': message})

    async def select_my_messages(self, chat_id):
        """
        TODO
        :param chat_id:
        :return: TODO
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search((where('type') == DBType.MESSAGES.value) &
                                (where('chat_id') == chat_id))

    async def insert_contact(self, owner_id, user_id, encrypted_alias):
        """
        Inserts a contact into the database.
        :param owner_id:
        :param user_id:
        :param encrypted_alias:
        :return: 0 if the user was successfully inserted, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if (my_db.contains(
                    (where('type') == DBType.CONTACTS.value) & (where('owner_id') == owner_id) &
                    (where('user_id') == user_id))):
                raise DatabaseError(reason=
                                    'Can not insert contact into the database. User with ID '
                                    '{} already exist in the cotacts for the user with ID {}.'
                                    .format(user_id, owner_id))
            my_db.insert({'type': DBType.CONTACTS.value, 'owner_id': owner_id,
                          'user_id': user_id, 'alias': encrypted_alias})

    async def select_my_contacts(self, owner_id):
        """
        TODO
        :param owner_id:
        :return: TODO
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search(
                (where('type') == DBType.CONTACTS.value) &
                (where('owner_id') == owner_id))

    async def delete_my_contact(self, owner_id, user_id):
        "Delete contact of the selected user."
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.remove(
                (where('type') == DBType.CONTACTS.value) & (where('owner_id') == owner_id) &
                (where('user_id') == user_id))

    async def alter_my_contact(self, owner_id, user_id, new_alias):
        """
        Alters the contact for the specified user.
        :param owner_id:
        :param user_id:
        :param new_alias:
        :return: TODO
        """
        async with AIOTinyDB(self.db_string) as my_db:
            results = my_db.search(
                (where('type') == DBType.CONTACTS.value) &
                (where('owner_id') == owner_id) &
                (where('user_id') == user_id))
            for result in results:
                result['alias'] = new_alias
            my_db.write_back(results)


if __name__ == "__main__":
    DATABASE = DB()
    LOOP = asyncio.new_event_loop()

    USER1 = {'user_id': 123, 'pkenc': 'pkenc_data', 'pksig': 'pksig_data'}
    USER2 = {'user_id': 123456, 'pkenc': 'pkenc_data2', 'pksig': 'pksig_data2'}
    CONTACT1 = {'owner_id': USER1.get('user_id'),
                'user_id': USER2.get('user_id'),
                'encrypted_alias': 'USER2 in contacts of USER1'}
    CONTACT2 = {'owner_id': USER2.get('user_id'),
                'user_id': USER1.get('user_id'),
                'encrypted_alias': 'USER1 in contacts of USER2'}

    LOOP.run_until_complete(DATABASE.insert_user(USER1.get('user_id'),
                                                 USER1.get('pkenc'), USER1.get('pksig')))
    try:
        LOOP.run_until_complete(DATABASE.insert_user(USER1.get('user_id'),
                                                     USER1.get('pkenc'), USER1.get('pksig')))
    except DatabaseError:
        print('Duplicate user won\'t be added.')

    LOOP.run_until_complete(DATABASE.insert_user(USER2.get('user_id'),
                                                 USER2.get('pkenc'), USER2.get('pksig')))

    GET_USER2 = LOOP.run_until_complete(DATABASE.select_user(USER2.get('user_id')))[0]
    print(GET_USER2)

    LOOP.run_until_complete(DATABASE.insert_contact(CONTACT1.get('owner_id'),
                                                    CONTACT1.get('user_id'),
                                                    CONTACT1.get('encrypted_alias')))
    LOOP.run_until_complete(DATABASE.insert_contact(CONTACT2.get('owner_id'),
                                                    CONTACT2.get('user_id'),
                                                    CONTACT2.get('encrypted_alias')))
    try:
        LOOP.run_until_complete(DATABASE.insert_contact(CONTACT1.get('owner_id'),
                                                        CONTACT1.get('user_id'),
                                                        CONTACT1.get('encrypted_alias')))
    except DatabaseError:
        print('Duplicate contact won\'t be added')

    print(LOOP.run_until_complete(DATABASE.select_my_contacts(USER2.get('user_id'))))

    ALTERED_FIELD = 'changed_encrypted_alias'
    LOOP.run_until_complete(DATABASE.alter_my_contact(CONTACT2.get('owner_id'),
                                                      CONTACT2.get('user_id'),
                                                      ALTERED_FIELD))

    RESULT = LOOP.run_until_complete(DATABASE.select_my_contacts(USER2.get('user_id')))
    assert RESULT[0].pop('alias') == ALTERED_FIELD
    LOOP.close()
