from tinydb import TinyDB, Query, where
import asyncio
from aiotinydb import AIOTinyDB
import time
import rsa
import json
#TYPES
#1: users
#2: chats
#3: messages
#4: contacts

#returning 0 from method means everything is ok
#returning 1 means something is wrong :D 

#all selects return strings


class DB:

    dbString = "db.json"
    query = Query()
    
    def DB(self):
        print("Database created");

    async def insertUser(self, userID, publicKeyEnc, publicKeySig):
        async with AIOTinyDB(self.dbString) as db:
            if(True != db.contains((where('type') == 1) & (where('id') == userID))):
                db.insert({'type': 1, 'id': userID, 'publicKeyEnc': publicKeyEnc, 'publicKeySig': publicKeySig})
            else:
                return "Error appeared when inserting new user"

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

    async def insertMessage(self, messageID, chatID, senderID, timestamp, message):
        async with AIOTinyDB(dbString) as db:
            db.insert({'type': 3, 'id': messageID, 'chatID': chatID, 'senderID': senderID, 'timestamp': time.time(), 'message': message})

    async def selectMyMessages(self, chatID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 3) & (where('chatID') == myID))

    async def insertContact(self, contactID, ownerID, userID, encryptedAlias):
        async with AIOTinyDB(self.dbString) as db:
            if(True == db.contains((where('type') == 4) & (where('ownerID') == ownerID) & (where('userID') == userID))):
                return 1
            else:
                db.insert({'type': 4, 'id': contactID, 'ownerID': ownerID, 'userID': userID, 'alias': encryptedAlias})
                return 0
        
    async def selectMyContacts(self, ownerID):
        async with AIOTinyDB(self.dbString) as db:
            return db.search((where('type') == 4) & (where('ownerID') == ownerID))

    async def inputValidation(self, publicKey, sign, hash):
        return 0
        

database = DB()
loop = asyncio.new_event_loop()
print(loop.run_until_complete(database.selectChat(123456)))
loop.close()

