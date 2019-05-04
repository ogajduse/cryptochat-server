# API Documentation

API is reachable on http://<ip address>:8888/api/

## /api/contacts
* **GET**
  ```json
    "owner_id": {"type": "integer"}
  ```
* **POST**
  ```json
   "owner_id":{
      "type":"integer"
   },
   "user_id":{
      "type":"integer"
   },
   "encrypted_alias":{
      "type":"string"
   }
  ```

## /api/chats/user
* **GET**
  ```json
    "user_id": {"type": "integer"}
  ```

## /api/chats
* **GET**
  ```json
    "chat_id": {"type": "integer"}
  ```
* **POST**
  ```json
  "users":{
      "type":"array",
      "items":{
         "type":"integer"
      }
   },
   "sym_key_enc_by_owners_pub_keys":{
      "type":"array",
      "items":{
         "type":"string"
      }
   }
  ```

## /api/users
* **GET**
  ```json
    "user_id": {"type": "integer"}
  ```
* **POST**
  ```json
   "user_id":{
      "type":"integer"
   },
   "public_key":{
      "type":"string"
   }
  ```
  
## /api/message/new
* **POST**
  ```json
   "chat_id":{
      "type":"integer"
   },
   "sender_id":{
      "type":"integer"
   },
   "message":{
      "type":"string"
   },
   "hash":{
      "type":"integer"
   }
  ```
  
## /api/message/updates
* **POST**
  ```json
   "cursor":{
      "type":"number"
   },
   "chat_id":{
      "type":"integer"
   }
  ```
  
