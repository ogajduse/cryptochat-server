import rsa


def rsa_verification(public_key_of_receiver, signature, block_bits):
    boolean_value = rsa.verify(block_bits, signature, public_key_of_receiver)
    if boolean_value:
        return True
    else:
        return False
