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


def _store_object(content: bytes, tinygit_dir: str) -> str:
    sha1hash = hashlib.sha1(content).hexdigest()

    dirname, filename = sha1hash[:2], sha1hash[2:]

    compressed = zlib.compress(content)

    dirpath = os.path.join(tinygit_dir, "objects", dirname)
    os.makedirs(dirpath, exist_ok=True)

    with open(os.path.join(dirpath, filename), "wb") as file:
        file.write(compressed)

    return sha1hash


def write_blob(data: bytes, tinygit_dir=".tinygit") -> str:
    store_content = f"blob {len(data)}\0".encode()
    store_content += data

    return _store_object(store_content, tinygit_dir)


def write_tree(entries: list[tuple[str, str, str]], tinygit_dir=".tinygit") -> str:
    tree_content = b""
    for entry in entries:
        tree_content += f"{entry[0]} {entry[1]}\0".encode()
        tree_content += bytes.fromhex(entry[2])

    store_content = f"tree {len(tree_content)}\0".encode()
    store_content += tree_content

    return _store_object(store_content, tinygit_dir)
