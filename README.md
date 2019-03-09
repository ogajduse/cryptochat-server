# cryptochat-server

Server side for Cryptochat.

Transation for creation of schema of FlureeDB database

[{
 "_id": "_collection",
 "name": "users"
},{
    "_id": "_predicate",
    "name": "users/id",
    "type": "long",
    "unique": true
},{
    "_id": "_predicate",
    "name": "users/publicKeyEnc",
    "type": "string",
    "unique": true
},{
    "_id": "_predicate",
    "name": "users/publicKeySig",
    "type": "string",
    "unique": true
},

{
 "_id": "_collection",
 "name": "chats"
},{
    "_id": "_predicate",
    "name": "chats/id",
    "type": "long",
    "unique": true
},{
    "_id": "_predicate",
    "name": "chats/usersInConversation",
    "type": "ref",
    "restrictCollection": "users",
    "multi": true
},{
    "_id": "_predicate",
    "name": "users/encryptedKeys",
    "type": "string",
    "multi": true
},

{
 "_id": "_collection",
 "name": "messages"
},{
    "_id": "_predicate",
    "name": "messages/chatId",
    "type": "ref",
    "restrictCollection": "chats"
},{
    "_id": "_predicate",
    "name": "messages/sender",
    "type": "ref",
    "restrictCollection": "users"
},{
    "_id": "_predicate",
    "name": "messages/message",
    "type": "string"
},{
    "_id": "_predicate",
    "name": "messages/timestamp",
    "type": "instant"
},

{
 "_id": "_collection",
 "name": "contacts"
},{
    "_id": "_predicate",
    "name": "contacts/owner",
    "type": "ref",
    "restrictCollection": "users"
},{
    "_id": "_predicate",
    "name": "contacts/user",
    "type": "ref",
    "restrictCollection": "users"
},{
    "_id": "_predicate",
    "name": "contacts/alias",
    "type": "string"
}]
