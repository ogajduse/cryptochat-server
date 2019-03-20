from tinydb import TinyDB, Query, where
import asyncio
from aiotinydb import AIOTinyDB
import time
import rsa
import json
import hashlib
#TYPES
#1: users
#2: chats
#3: messages
#4: contacts

DB_TYPE_USERS = 1
DB_TYPE_CHATS = 2
DB_TYPE_MESSAGES = 3
DB_TYPE_CONTACTS =4

#returning 0 from method means everything is ok
#returning 1 means something is wrong :D 

#all selects return strings

#Validation function for database inputs
def inputValidator(self, publicKey, sign, jsonData):
    digest = hashlib.sha512(jsonData.encode('utf8')).hexdigest()
    digestDecrypted = rsa.decrypt(sign, publicKey)
    if(digest == digestDecrypted):
        return 0
    else:
        return 1

class DB:

    def __init__(self):
        self.dbString = "db.json"
        self.query = Query()
        print("Database created")

    async def insertUser(self, userID, publicKeyEnc, publicKeySig):
        async with AIOTinyDB(self.dbString) as db:
            if(True != db.contains((where('type') == 1) & (where('id') == userID))):
                db.insert({'type': 1, 'id': userID, 'publicKeyEnc': publicKeyEnc, 'publicKeySig': publicKeySig})
            else:
                return 1
            return 0

    async def selectUser(self, userID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 1) & (where('id') == userID))

    async def insertChat(self, chatID, owner, users, usersPublicKeys):
        async with AIOTinyDB(self.dbString) as db:
            if(False == db.contains((where('type') == 2) & ((where('id') == chatID) | (where('users').all(users))))):
                db.insert({'type': 2, 'id': chatID, 'owner': owner, 'users': users, 'usersPublicKey': usersPublicKeys})
                return 0
            else:
                return 1

    async def selectChat(self, chatID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 2) & (where('id') == chatID))

    async def selectMyChats(self, myID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 2) & ((where('users').any([myID])) | (where('owner') == myID)) )

    async def insertMessage(self, chatID, senderID, timestamp, message):
        async with AIOTinyDB(dbString) as db:
            db.insert({'type': 3, 'chatID': chatID, 'senderID': senderID, 'timestamp': time.time(), 'message': message})

    async def selectMyMessages(self, chatID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 3) & (where('chatID') == myID))

    async def insertContact(self, ownerID, userID, encryptedAlias):
        async with AIOTinyDB(self.dbString) as db:
            if(True == db.contains((where('type') == 4) & (where('ownerID') == ownerID) & (where('userID') == userID))):
                return 1
            else:
                db.insert({'type': 4, 'ownerID': ownerID, 'userID': userID, 'alias': encryptedAlias})
                return 0
        
    async def selectMyContacts(self, ownerID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 4) & (where('ownerID') == ownerID))

    async def deleteMyContact(self, ownerID, userID):
        async with AIOTinyDB(self.dbString) as db:
            return db.remove((where('type') == 4) & (where('ownerID') == ownerID) & (where('userID') == userID))

    async def alterMyContact(self, ownerID, userID, newAlias):
        async with AIOTinyDB(self.dbString) as db:
            results = db.search((where('type') == 4) & (where('ownerID') == ownerID) & (where('userID') == userID))
            for result in results:
                result['alias'] = newAlias
            db.write_back(results)


database = DB()
loop = asyncio.new_event_loop()
print(loop.run_until_complete(database.insertContact(123456, 1234567, "Sranda" )))
print(loop.run_until_complete(database.selectMyContacts(123456)))
print(loop.run_until_complete(database.alterMyContact(123456,1234567, "Prdel")))
print(loop.run_until_complete(database.selectMyContacts(123456)))
loop.close()

