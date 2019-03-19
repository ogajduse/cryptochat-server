from tinydb import TinyDB, Query, where
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

    db = TinyDB('db.json')
    query = Query()
    def DB(self):
        print("Database created");

    def insertUser(self, userID, publicKeyEnc, publicKeySig):
        if(True != self.db.contains((where('type') == 1) & (where('id') == userID))):
            self.db.insert({'type': 1, 'id': userID, 'publicKeyEnc': publicKeyEnc, 'publicKeySig': publicKeySig})
        else:
            return "Error appeared when inserting new user"

    def selectUser(self, userID):
        return self.db.search((where('type') == 1) & (where('id') == userID))

    def insertChat(self, chatID, owner, users, usersPublicKeys):
        if(False == self.db.contains((where('type') == 2) & ((where('id') == chatID) | (where('users').all(users))))):
            self.db.insert({'type': 2, 'id': chatID, 'owner': owner, 'users': users, 'usersPublicKey': usersPublicKeys})
            return 0
        else:
            return 1

    def selectChat(self, chatID):
        return self.db.search((where('type') == 2) & (where('id') == chatID))

    def selectMyChats(self, myID):
        return self.db.search((where('type') == 2) & ((where('users').any([myID])) | (where('owner') == myID)) )

    def insertMessage(self, messageID, chatID, senderID, timestamp, message):
        self.db.insert({'type': 3, 'id': messageID, 'chatID': chatID, 'senderID': senderID, 'timestamp': time.time(), 'message': message})

    def selectMyMessages(self, chatID):
        return self.db.search((where('type') == 3) & (where('chatID') == myID))

    def insertContact(self, contactID, ownerID, userID, encryptedAlias):
        if(True == self.db.contains((where('type') == 4) & (where('ownerID') == ownerID) & (where('userID') == userID))):
            return 1
        else:
            self.db.insert({'type': 4, 'id': contactID, 'ownerID': ownerID, 'userID': userID, 'alias': encryptedAlias})
            return 0
        
    def selectMyContacts(self, ownerID):
        return self.db.search((where('type') == 4) & (where('ownerID') == ownerID))

    def inputValidation(self, publicKey, sign, hash):
        return 0
        


