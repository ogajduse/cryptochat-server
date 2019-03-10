# cryptochat-server

Server side for Cryptochat.

Transation for creation of schema of FlureeDB database:

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
    "name": "chats/encryptedKeys",
    "type": "string",
    "multi": true
},

{
 "_id": "_collection",
 "name": "messages"
},{
    "_id": "_predicate",
    "name": "messages/id",
    "type": "long",
    "unique": true
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

Add user to database:

[{
  "_id":  "users$1234567123",
  "id":   1234567123,
  "publicKeySig": "12312312312112333",
  "publicKeyEnc": "123123123123123333"
}]

Add chat to database with users:

[{
  "_id": "chats$123",
  "id":   123,
  "usersInConversation": [351843720888321],
  "encryptedKeys": ["1asdassdsads"]
}]

Add message to chat in database:

[{
  "_id": "message",
  "id": 1234
  "chatId":   1234567,
  "sender": 351843720888321,
  "message": "123123123123"
  "timestamp": #(now)
}]

Add contact into users:

[{
  "_id":      "contacts",
  "id":   1234567,
  "publicKeySig": "123123123121",
  "publicKeyEnc": "123123123123"
}]
