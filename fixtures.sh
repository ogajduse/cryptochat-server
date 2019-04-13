# insert user1
curl http://localhost:8888/api/users -X 'POST' -H 'Content-Type: application-json' --data '{"user_id": 123, "public_key":"public_key_data"}' | jq .

# insert user2
curl http://localhost:8888/api/users -X 'POST' -H 'Content-Type: application-json' --data '{"user_id": 123456, "public_key":"public_key_data2"}' | jq .

# insert contact1
curl http://localhost:8888/api/contacts -X 'POST' -H 'Content-Type: application-json' --data '{"owner_id": 123, "user_id": 123456, "encrypted_alias": "USER2 in contacts of USER1"}' | jq .

# insert contact2
curl http://localhost:8888/api/contacts -X 'POST' -H 'Content-Type: application-json' --data '{"owner_id": 123456, "user_id": 123, "encrypted_alias": "USER1 in contacts of USER2"}' | jq .

# insert chat1
curl http://localhost:8888/api/chats -X 'POST' -H 'Content-Type: application-json' --data '{"users": [123, 123456], "sym_key_enc_by_owners_pub_keys": ["pkenc_data", "pkenc_data2"]}' | jq .

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123, "message": "Hi there!"}' | jq .

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123456, "message": "Oh hi! I have some news for you!"}' | jq .

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123, "message": "I am curious, tell me..."}' | jq .

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123456, "message": "We are not real... :-("}' | jq .
