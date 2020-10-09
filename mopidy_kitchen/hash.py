from hashlib import md5


def make_hash(string: str):
    if not isinstance(string, str):
        raise TypeError("Not a string: %s" % string)
    return md5(string.encode()).hexdigest()
