# cryptochat-server

Server side for Cryptochat.

Create DB SQL:
CREATE DATABASE securedChat;

CREATE TABLES SQL:
CREATE TABLE securedChat.users(id INT PRIMARY KEY NOT NULL UNIQUE, publicKeyEnc BYTES, publicKeySig BYTES);                                                                                                                                     CREATE TABLE securedChat.chats(id SERIAL PRIMARY KEY UNIQUE,users int[], keys BYTES[], sign BYTES);                                                                                                                                                         CREATE TABLE securedChat.messages(id SERIAL PRIMARY KEY UNIQUE, chat_id int references securedChat.chats(id), sender_id int references securedChat.users(id), message BYTES , sign BYTES);                                                                                                                                                  CREATE TABLE securedChat.contacts(id SERIAL PRIMARY KEY UNIQUE, contact_owner_id int references securedChat.users(id), contact_id int references securedChat.users(id), alias STRING, sign BYTES);                                                                                                                                          CREATE TABLE securedChat.server(id SERIAL PRIMARY KEY, domain STRING UNIQUE);


INSERT TO DB EXAMPLES:

INSERT INTO securedChat.server (domain) VALUES ('mkriProjekt5.local');

INSERT INTO securedChat.users (id , publicKeyEnc, publicKeySig) VALUES (123456, b'\100', b'\100');

INSERT INTO securedChat.chats (users, keys, sign) VALUES (ARRAY[1,2,3,4], ARRAY[b'\100', b'\120', b'\130', b'\125'], b'\100');

INSERT INTO securedChat.messages (chat_id, sender_id, message, sign) VALUES (431349324557844481, 123456, b'\100\100', b'\100\100');

INSERT INTO securedChat.contacts (contact_owner_id, securedChat.users, alias, sign) VALUES (123456, 1234567, "Zahorak", b'\100');

SELECTS FROM DB EXAMPLES:

SELECT * FROM securedChat.***;

SELECT * FROM securedChat.users WHERE id = 123456;
