"""
Module to handle database calls.
"""

import asyncio
import hashlib
import os
import time
from enum import Enum

import numpy
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

    async def insert_user(self, user_id, public_key):
        """
        Insert a new user to database.
        :param user_id: Users ID
        :param public_key: Public key of user
        :return: 0 if the user was added, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if my_db.contains((where('type') == DBType.USERS.value) & (where('id') == user_id)):
                raise DatabaseError(reason=
                                    'Can not insert user into the database. '
                                    'User with ID "{}" already exist.'.format(user_id))

            if await self.user_pubkey_exist(public_key):
                raise DatabaseError(reason='Can not insert user into the database. '
                                           'User with public key "{}" already exist.'
                                    .format(public_key))
            my_db.insert({'type': DBType.USERS.value,
                          'id': user_id,
                          'public_key': public_key})

            return

    async def select_user(self, user_id):
        """
        Return the user that was searched.
        :param user_id: Users ID
        :return: user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.get((where('type') == DBType.USERS.value) & (where('id') == user_id))

    async def user_pubkey_exist(self, pubkey):
        """Check if the given pubkey exist in the database.
        :param pubkey: Public key of the user
        :return: True if the public key is found in the database, false otherwise
        """
        async with AIOTinyDB(self.db_string) as my_db:
            exist = my_db.contains((where('type') == DBType.USERS.value) &
                                   (where('public_key') == pubkey))
            return exist

    async def select_all_user_ids(self):
        """
        Get all user ids and return them.
        :return: array: all user IDs stored in the database in
        """
        async with AIOTinyDB(self.db_string) as my_db:
            all_users = my_db.search(where('type') == DBType.USERS.value)
            user_ids = []
            for user in all_users:
                user_ids.append(user['id'])
            return user_ids

    async def insert_chat(self, users, sym_key_enc_by_owners_pub_keys):
        """
        Inserts the new entry to the particular chat.
        :param users: IDs of users in chat
        :param sym_key_enc_by_owners_pub_keys: encrypted symmetric keys using public keys of user
        :return: 0 if the chat was inserted into the database, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            chat_id = await self.get_last_chat() + 1
            all_user_ids = await self.select_all_user_ids()
            try:
                # check that the users are present in the DB
                assert set(users).issubset(all_user_ids)
            except AssertionError:
                # show which users are not in the DB
                all_user_ids_str = [str(x) for x in all_user_ids]
                users_str = [str(x) for x in users]
                users_diff = ','.join(numpy.setdiff1d(users_str, all_user_ids_str))
                raise DatabaseError(reason=
                                    'Can not insert chat into the database. '
                                    'User/users {} not found in the database.'.format(users_diff))
            # check for the duplicate chats
            if my_db.contains((where('type') == DBType.CHATS.value) &
                              (where('users').all(users))):
                raise DatabaseError(reason=
                                    'Can not insert chat into the database. '
                                    'Chat with users "{}" already exist.'
                                    .format(','.join(str(x) for x in users)))

            try:
                # check if we have the same count for users as for symmetric keys
                assert len(users) == len(sym_key_enc_by_owners_pub_keys)
            except AssertionError:
                raise DatabaseError(reason=
                                    'Can not insert chat into the database. '
                                    'Number of users should be the same as number of '
                                    'symmetric keys.')

            my_db.insert({'type': DBType.CHATS.value,
                          'id': chat_id,
                          'users': users,
                          'sym_key_enc_by_owners_pub_keys': sym_key_enc_by_owners_pub_keys})

    async def select_chat(self, chat_id):
        """
        Return the chat ID that was searched for.
        :param chat_id: ID of chat
        :return: Chat that was searched for user's id
        """
        async with AIOTinyDB(self.db_string) as my_db:
            db_response = my_db.get((where('type') == DBType.CHATS.value) &
                                    (where('id') == chat_id))
            if not db_response:
                raise DatabaseError(reason='Chat with ID {} does not exist in the database.'
                                    .format(chat_id))
            return db_response

    async def select_my_chats(self, my_id):
        """
        Return the chats for the particular user.
        :param my_id: User ID
        :return: Chats ID for the particular user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not await self.chat_id_exist(my_id):
                raise DatabaseError(reason='User with ID {} not found in the database.')
            return my_db.search(
                (where('type') == DBType.CHATS.value) & ((where('users').any([my_id]))))

    async def get_last_chat(self):
        """
        Get the last ID of chat in the database.
        :return: ID of the last inserted chat
        """
        return await self.__get_last_entity_id(DBType.CHATS, 'id')

    async def chat_id_exist(self, chat_id):
        """
        Check whether the chat exist.
        :return: true if the chat exist, false otherwise
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.contains((where('type') == DBType.CHATS.value) &
                                  (where('id') == chat_id))

    async def insert_message(self, chat_id, sender_id, message):
        """
        Insert a message into the chat.
        :param chat_id: Chat of ID
        :param sender_id: ID of user that sends message
        :param message: Message content (encrypted)
        :return: Returns nothing
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not await self.select_user(sender_id):
                raise DatabaseError(reason='User with ID {} not found in the database.'
                                    .format(sender_id))
            if not await self.chat_id_exist(chat_id):
                raise DatabaseError(reason='Chat with ID {} not found in the database.'
                                    .format(chat_id))
            my_db.insert({'type': DBType.MESSAGES.value,
                          'chat_id': chat_id,
                          'sender_id': sender_id,
                          'timestamp': time.time(),
                          'message': message})

    async def select_my_messages(self, chat_id):
        """
        TODO
        :param chat_id: ID of chat
        :return: Returns json of all messages in chat
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not await self.chat_id_exist(chat_id):
                raise DatabaseError(reason='Chat with ID {} not found in the database.'
                                    .format(chat_id))
            return my_db.search((where('type') == DBType.MESSAGES.value) &
                                (where('chat_id') == chat_id))

    async def insert_contact(self, owner_id, user_id, encrypted_alias):
        """
        Inserts a contact into the database.
        :param owner_id: ID of user
        :param user_id: ID of contact.
        :param encrypted_alias: Encrypted alias of contact
        :return: 0 if the user was successfully inserted, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if (my_db.contains(
                    (where('type') == DBType.CONTACTS.value) & (where('owner_id') == owner_id) &
                    (where('user_id') == user_id))):
                raise DatabaseError(reason=
                                    'Can not insert contact into the database. User with ID '
                                    '{} already exist in the contacts for the user with ID {}.'
                                    .format(user_id, owner_id))
            if not await self.select_user(owner_id):
                raise DatabaseError(reason=
                                    'Can not insert contact into the database. User with ID '
                                    '{} does not exist in the database.'.format(owner_id))
            if not await self.select_user(user_id):
                raise DatabaseError(reason=
                                    'Can not insert contact into the database. User with ID '
                                    '{} does not exist in the database.'.format(user_id))
            my_db.insert({'type': DBType.CONTACTS.value, 'owner_id': owner_id,
                          'user_id': user_id, 'alias': encrypted_alias})

    async def select_my_contacts(self, owner_id):
        """
        TODO
        :param owner_id: User ID which wants his contacts.
        :return: Returns user's contacts in json.
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not await self.select_user(owner_id):
                raise DatabaseError(reason='User with ID {} does not exist in the database.'
                                    .format(owner_id))
            return my_db.search((where('type') == DBType.CONTACTS.value)
                                & (where('owner_id') == owner_id))

    async def delete_my_contact(self, owner_id, user_id):
        """Delete contact of the selected user."""
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.remove(
                (where('type') == DBType.CONTACTS.value) & (where('owner_id') == owner_id) &
                (where('user_id') == user_id))

    async def alter_my_contact(self, owner_id, user_id, new_alias):
        """
        Alters the contact for the specified user.
        :param owner_id: User ID which has this contact
        :param user_id: ID of user which is in contact
        :param new_alias: New alias for user in contact
        :return: Nothing
        """
        async with AIOTinyDB(self.db_string) as my_db:
            results = my_db.search(
                (where('type') == DBType.CONTACTS.value) &
                (where('owner_id') == owner_id) &
                (where('user_id') == user_id))
            for result in results:
                result['alias'] = new_alias
            my_db.write_back(results)

    async def __get_last_entity_id(self, entity, entity_id_name):
        async with AIOTinyDB(self.db_string) as my_db:
            db_search = my_db.search(where('type') == entity.value)
            if not db_search:
                return 0
            sorted_entities = sorted(db_search, key=lambda entity_id: entity_id[entity_id_name])
            return sorted_entities[-1].get(entity_id_name)


if __name__ == "__main__":
    DATABASE = DB()
    LOOP = asyncio.new_event_loop()

    USER1 = {'user_id': 123, 'public_key': 'public_key_data'}
    USER2 = {'user_id': 123456, 'public_key': 'public_key_data2'}
    CONTACT1 = {'owner_id': USER1.get('user_id'),
                'user_id': USER2.get('user_id'),
                'encrypted_alias': 'USER2 in contacts of USER1'}
    CONTACT2 = {'owner_id': USER2.get('user_id'),
                'user_id': USER1.get('user_id'),
                'encrypted_alias': 'USER1 in contacts of USER2'}
    CHAT1 = {'users': [USER1.get('user_id'), USER2.get('user_id')],
             'sym_key_enc_by_owners_pub_keys': [USER1.get('public_key_encrypted'),
                                                USER2.get('public_key_encrypted')]}
    MESSAGES = [{'chat_id': CHAT1.get('chat_id'),
                 'sender_id': CHAT1.get('users')[0],
                 'message': "Hi there!"},
                {'chat_id': CHAT1.get('chat_id'),
                 'sender_id': CHAT1.get('users')[1],
                 'message': 'Oh hi! I have some news for you!'},
                {'chat_id': CHAT1.get('chat_id'),
                 'sender_id': CHAT1.get('users')[0],
                 'message': 'I am curious, tell me...'},
                {'chat_id': CHAT1.get('chat_id'),
                 'sender_id': CHAT1.get('users')[1],
                 'message': 'We are not real... :-('}
                ]

    LOOP.run_until_complete(DATABASE.insert_user(USER1.get('user_id'),
                                                 USER1.get('public_key')))
    try:
        LOOP.run_until_complete(DATABASE.insert_user(USER1.get('user_id'),
                                                     USER1.get('public_key')))
    except DatabaseError:
        print('Duplicate user won\'t be added.')

    LOOP.run_until_complete(DATABASE.insert_user(USER2.get('user_id'),
                                                 USER2.get('public_key')))

    GET_USER2 = LOOP.run_until_complete(DATABASE.select_user(USER2.get('user_id')))
    print(GET_USER2)
    ASSERTION = GET_USER2.get('id') == USER2.get('user_id') and \
                GET_USER2.get('public_key') == USER2.get('public_key')
    assert ASSERTION

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

    RESULT = LOOP.run_until_complete(DATABASE.select_my_contacts(USER2.get('user_id')))
    print(RESULT[0])

    ALTERED_FIELD = CONTACT2.get('encrypted_alias') + '_changed'
    LOOP.run_until_complete(DATABASE.alter_my_contact(CONTACT2.get('owner_id'),
                                                      CONTACT2.get('user_id'),
                                                      ALTERED_FIELD))

    RESULT = LOOP.run_until_complete(DATABASE.select_my_contacts(USER2.get('user_id')))
    assert RESULT[0].pop('alias') == ALTERED_FIELD

    LOOP.run_until_complete(DATABASE.delete_my_contact(CONTACT1.get('owner_id'),
                                                       CONTACT1.get('user_id')))

    LOOP.run_until_complete(DATABASE.insert_chat(CHAT1.get('users'),
                                                 CHAT1.get('sym_key_enc_by_owners_pub_keys')))

    try:
        LOOP.run_until_complete(DATABASE.insert_chat(CHAT1.get('users'),
                                                     CHAT1.get('sym_key_enc_by_owners_pub_keys')))
    except DatabaseError:
        print('Duplicate chat won\'t be added')

    GET_USER_CHATS = LOOP.run_until_complete(DATABASE.select_my_chats(USER1.get('user_id')))
    USER_FIRST_CHAT = GET_USER_CHATS[0]
    GET_CHAT1 = LOOP.run_until_complete(DATABASE.select_chat(USER_FIRST_CHAT.get('id')))
    ASSERTION = GET_CHAT1.get('id') == USER_FIRST_CHAT.get('id') and \
                GET_CHAT1.get('users') == USER_FIRST_CHAT.get('users') and \
                GET_CHAT1.get('sym_key_enc_by_owners_pub_keys') == \
                USER_FIRST_CHAT.get('sym_key_enc_by_owners_pub_keys')
    assert ASSERTION
    assert USER_FIRST_CHAT == GET_CHAT1

    for it_message in MESSAGES:
        LOOP.run_until_complete(DATABASE.insert_message(it_message.get('chat_id'),
                                                        it_message.get('sender_id'),
                                                        it_message.get('message')))

    RESULT = LOOP.run_until_complete(DATABASE.select_my_messages(CHAT1.get('chat_id')))
    RESULT.sort(key=lambda x: x.get('timestamp'))

    for idx, it_message in enumerate(RESULT):
        assert it_message.get('chat_id') == MESSAGES[idx].get('chat_id')
        assert it_message.get('sender_id') == MESSAGES[idx].get('sender_id')
        assert it_message.get('message') == MESSAGES[idx].get('message')

    LOOP.close()
