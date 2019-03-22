"""
Module to handle database calls.
"""

import asyncio
import hashlib
import time

import rsa
from aiotinydb import AIOTinyDB
from tinydb import Query, where

# TYPES
# 1: users
# 2: chats
# 3: messages
# 4: contacts

DB_TYPE_USERS = 1
DB_TYPE_CHATS = 2
DB_TYPE_MESSAGES = 3
DB_TYPE_CONTACTS = 4


# returning 0 from method means everything is ok
# returning 1 means something is wrong :D

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


class DB:
    """
    Database class for handling the database queries
    """
    def __init__(self):
        self.db_string = "my_db.json"
        self.query = Query()
        print("Database created")

    async def insert_user(self, user_id, public_key_enc, public_key_sig):
        """
        Insert a new user to database.
        :param user_id:
        :param public_key_enc:
        :param public_key_sig:
        :return: 0 if the user was added, else 1
        """
        async with AIOTinyDB(self.db_string) as my_db:
            if not my_db.contains((where('type')) == 1 & (where('id') == user_id)):
                my_db.insert({'type': 1,
                              'id': user_id,
                              'public_key_enc': public_key_enc,
                              'public_key_sig': public_key_sig})
            else:
                return 1
            return 0

    async def select_user(self, user_id):
        """
        Return the user that was searched.
        :param user_id:
        :return: user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search((where('type') == 1) & (where('id') == user_id))

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
            if not my_db.contains((where('type') == 2) & ((where('id') == chat_id) |
                                                          (where('users').all(users)))):
                my_db.insert({'type': 2, 'id': chat_id, 'owner': owner,
                              'users': users, 'users_public_key': users_public_keys})
                return 0
            return 1

    async def select_chat(self, chat_id):
        """
        Return the chat ID that was searched for.
        :param chat_id:
        :return: Chat that was searched for
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search((where('type') == 2) & (where('id') == chat_id))

    async def select_my_chats(self, my_id):
        """
        Return the chats for the particular user.
        :param my_id:
        :return: Chats for the particular user
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search(
                (where('type') == 2) & ((where('users').any([my_id])) |
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
            my_db.insert({'type': 3,
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
            return my_db.search((where('type') == 3) & (where('chat_id') == chat_id))

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
                    (where('type') == 4) & (where('owner_id') == owner_id) &
                    (where('user_id') == user_id))):
                return 1
            my_db.insert({'type': 4, 'owner_id': owner_id,
                          'user_id': user_id, 'alias': encrypted_alias})
            return 0

    async def select_my_contacts(self, owner_id):
        """
        TODO
        :param owner_id:
        :return: TODO
        """
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.search(
                (where('type') == 4) &
                (where('owner_id') == owner_id))

    async def delete_my_contact(self, owner_id, user_id):
        "Delete contact of the selected user."
        async with AIOTinyDB(self.db_string) as my_db:
            return my_db.remove(
                (where('type') == 4) & (where('owner_id') == owner_id) &
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
                (where('type') == 4) &
                (where('owner_id') == owner_id) &
                (where('user_id') == user_id))
            for result in results:
                result['alias'] = new_alias
            my_db.write_back(results)


if __name__ == "__main__":
    DATABASE = DB()
    LOOP = asyncio.new_event_loop()
    print(LOOP.run_until_complete(DATABASE.insert_user(123, "pkenc", "pksig")))
    print(
        LOOP.run_until_complete(
            DATABASE.insert_user(
                123456,
                1234567,
                "Sranda")))
    print(
        LOOP.run_until_complete(
            DATABASE.insert_contact(
                123456,
                1234567,
                "Sranda")))
    print(LOOP.run_until_complete(DATABASE.select_my_contacts(123456)))
    print(
        LOOP.run_until_complete(
            DATABASE.alter_my_contact(
                123456,
                1234567,
                "Prdel")))
    print(LOOP.run_until_complete(DATABASE.select_my_contacts(123456)))
    LOOP.close()
