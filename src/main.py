import hashlib
import os
import zlib


def init(path=".") -> None:
    base = os.path.join(path, ".tinygit")
    objects = os.path.join(base, "objects")
    refs_heads = os.path.join(base, "refs", "heads")
    paths = [base, objects, refs_heads]
    for p in paths:
        os.makedirs(p, exist_ok=True)

    with open(os.path.join(base, "HEAD"), "w") as head:
        head.write("ref: refs/heads/main\n")

    return


def write_object(data: bytes, tinygit_dir=".tinygit") -> str:
    store_content = b"blob "
    store_content += str(len(data)).encode()
    store_content += b"\0"
    store_content += data

    sha1hash = hashlib.sha1(store_content).hexdigest()

    dirname, filename = sha1hash[:2], sha1hash[2:]

    compressed = zlib.compress(store_content)

    dirpath = os.path.join(tinygit_dir, "objects", dirname)
    os.makedirs(dirpath, exist_ok=True)

    with open(os.path.join(dirpath, filename), "wb") as file:
        file.write(compressed)

    return sha1hash
