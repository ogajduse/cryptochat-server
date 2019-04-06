# insert user1
curl http://localhost:8888/api/users -X 'POST' -H 'Content-Type: application-json' --data '{"user_id": 123, "public_key_enc":"pkenc_data", "public_key_sig": "pksig_data"}'

# insert user2
curl http://localhost:8888/api/users -X 'POST' -H 'Content-Type: application-json' --data '{"user_id": 123456, "public_key_enc":"pkenc_data2", "public_key_sig": "pksig_data2"}'

# insert contact1
curl http://localhost:8888/api/contacts -X 'POST' -H 'Content-Type: application-json' --data '{"owner_id": 123, "user_id": 123456, "encrypted_alias": "USER2 in contacts of USER1"}'

# insert contact2
curl http://localhost:8888/api/contacts -X 'POST' -H 'Content-Type: application-json' --data '{"owner_id": 123456, "user_id": 123, "encrypted_alias": "USER1 in contacts of USER2"}'

# insert chat1
curl http://localhost:8888/api/chats -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "owner": 123, "users": [123, 123456], "users_public_key": ["pkenc_data", "pkenc_data2"]}'

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123, "message": "Hi there!"}'

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123456, "message": "Oh hi! I have some news for you!"}'

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123, "message": "I am curious, tell me..."}'

# insert message
curl http://localhost:8888/api/message/new -X 'POST' -H 'Content-Type: application-json' --data '{"chat_id": 987, "sender_id": 123456, "message": "We are not real... :-("}'
