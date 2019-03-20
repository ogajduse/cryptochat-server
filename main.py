from tinydb import TinyDB, Query, where
import time
import rsa
import json

#usage examples


#RSA encryption example
(bob_pub, bob_priv) = rsa.newkeys(512)
message = 'hello Bob!'.encode('utf8')
crypto = rsa.encrypt(message, bob_pub)
#print(crypto)
message = rsa.decrypt(crypto, bob_priv)
#print(message.decode('utf8'))

import hashlib
#RSA signing example (public key and private keys are )
#
(bob_priv, bob_pub) = rsa.newkeys(512)
message = "hello Bob"
digest = hashlib.sha512(message.encode('utf8')).hexdigest()
#print(digest)
sign = rsa.encrypt(message.encode('utf8'), bob_priv)
digestDecrypted = rsa.decrypt(sign, bob_pub)
#print(digest)
#print(digestDecrypted)

        
db = DB();
#db.insertUser(123456,"123456", "123456")
#print(db.selectUser(123456))
db.insertChat(123456,123456,[123456789,123456789],[123456789,98796543])
db.insertChat(1234567,1234567,[123456,123456789],[123456789,98796543])
db.insertChat(1234568,1234568,[123456,123456789],[123456789,98796543])
#print(db.selectMyChats(123456))

db.insertContact(123456, 123456, 1234567, "Roland")
db.insertContact(1234567, 123456, 12345678, "Ondra")
db.insertContact(1234567, 123456, 123456789, "Sarka")
db.insertContact(1234567, 1234567, 123456789, "Sarka")
db.insertContact(1234567, 1234567, 123456789, "Sarka")

#print(db.selectMyContacts(123456))
#print(db.selectMyContacts(1234567))
    
# Insert new user
#db.insert({'type': 1, 'id': 123456, 'publicKeyEnc': "123456789", 'publicKeySig': '123456789')}
# Insert new chat
#db.insert({'type': 2, 'id': 123456, 'ownerID': 123456, 'users': [123456,123455], 'publicKeys': ["123456", "123456"]})


