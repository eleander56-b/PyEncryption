import os

def equalize(path_1, path_2):
    """
    Makes two files equal in size by padding the smaller file with random bytes.
    Also closes the files properly after reading.
    """
    with open(path_1, "rb") as f1:
        dat1 = f1.read()
    with open(path_2, "rb") as f2:
        dat2 = f2.read()

    l_dat1 = len(dat1)
    l_dat2 = len(dat2)

    if l_dat1 > l_dat2:
        dat2 += os.urandom(l_dat1 - l_dat2)
    else:
        dat1 += os.urandom(l_dat2 - l_dat1)

    with open(path_1, "wb") as out1:
        out1.write(dat1)
    with open(path_2, "wb") as out2:
        out2.write(dat2)

def keygen(orig_path, enc_path, key_path):
    """
    Generates a key by XORing two files. Uses equalize to make them the same size first.
    """
    equalize(orig_path, enc_path)
    with open(orig_path, "rb") as f_orig:
        original = f_orig.read()
    with open(enc_path, "rb") as f_enc:
        encrypted = f_enc.read()

    key = bytes(a ^ b for (a, b) in zip(original, encrypted))

    with open(key_path + enc_path + ".key", "wb") as key_out:
        key_out.write(key)

def decryptttt(enc_path, key_path, dec_path):
    """
    Decrypts a file using a key file.
    """
    with open(enc_path, "rb") as f_enc:
        encrypted = f_enc.read()
    with open(key_path, "rb") as f_key:
        key = f_key.read()

    decrypted = bytes(a ^ b for (a, b) in zip(encrypted, key))

    with open(dec_path, "wb") as decrypted_out:
        decrypted_out.write(decrypted)

    os.remove(key_path)
