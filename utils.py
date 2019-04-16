import rsa



def rsa_encryption(public_key_of_receiver, block_bits):
    """
    Sifrovani s public key prijemcu
    :param public_key_of_receiver:
    :param block_bits:
    :return:
    """
    message = block_bits.encode('utf8')  # dekodovani
    ciphertext = rsa.encrypt(message, public_key_of_receiver)  # zasifrovani pomocu public key
    return ciphertext


def rsa_decryption(private_key_of_owner, ciphertext):
    message = rsa.decrypt(ciphertext, private_key_of_owner)
    message.decode('utf8')
    return message