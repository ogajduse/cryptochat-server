"""
Tester for the database module
"""
import hashlib
import rsa

from db import DB


# pylint: disable=unused-variable,missing-docstring,too-many-function-args

def main():
    # usage examples

    # RSA encryption example`
    (bob_pub, bob_priv) = rsa.newkeys(512)
    message = 'hello Bob!'.encode('utf8')
    crypto = rsa.encrypt(message, bob_pub)
    # print(crypto)
    message = rsa.decrypt(crypto, bob_priv)
    # print(message.decode('utf8'))

    # RSA signing example (public key and private keys are )
    #
    (bob_priv, bob_pub) = rsa.newkeys(512)
    message = "hello Bob"
    digest = hashlib.sha512(message.encode('utf8')).hexdigest()
    # print(digest)
    sign = rsa.encrypt(message.encode('utf8'), bob_priv)
    digest_decrypted = rsa.decrypt(sign, bob_pub)
    # print(digest)
    # print(digestDecrypted)

    my_db = DB()
    # my_db.insertUser(123456,"123456", "123456")
    # print(my_db.selectUser(123456))
    my_db.insert_chat(123456, 123456, [123456789, 123456789], [123456789, 98796543])
    my_db.insert_chat(1234567, 1234567, [123456, 123456789], [123456789, 98796543])
    my_db.insert_chat(1234568, 1234568, [123456, 123456789], [123456789, 98796543])
    # print(my_db.select_my_chats(123456))

    my_db.insert_contact(123456, 123456, 1234567, "Roland")
    my_db.insert_contact(1234567, 123456, 12345678, "Ondra")
    my_db.insert_contact(1234567, 123456, 123456789, "Sarka")
    my_db.insert_contact(1234567, 1234567, 123456789, "Sarka")
    my_db.insert_contact(1234567, 1234567, 123456789, "Sarka")

    # print(my_db.select_my_contacts(123456))
    # print(my_db.select_my_contacts(1234567))

    # Insert new user
    # my_db.insert({'type': 1, 'id': 123456, 'publicKeyEnc': "123456789",
    #               'publicKeySig': '123456789'})
    # Insert new chat
    # my_db.insert({'type': 2, 'id': 123456, 'ownerID': 123456,
    #               'users': [123456,123455], 'publicKeys': ["123456", "123456"]})


if __name__ == "__main__":
    main()
