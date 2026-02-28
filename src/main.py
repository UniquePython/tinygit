import hashlib
import os
import zlib
from datetime import datetime, timezone


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


def write_commit(
    tree_hash: str, message: str, parent_hash: str | None = None, tinygit_dir=".tinygit"
) -> str:
    store_content = f"tree {tree_hash}\n"
    store_content += f"parent {parent_hash}\n" if parent_hash else ""

    timestamp = datetime.now(timezone.utc).timestamp()
    store_content += (
        f"author Ananyo Bhattacharya ananyobhattacharya10@gmail.com {timestamp}\n"
    )
    store_content += (
        f"committer Ananyo Bhattacharya ananyobhattacharya10@gmail.com {timestamp}\n\n"
    )

    store_content += message

    content = store_content.encode()
    full = f"commit {len(content)}\0".encode() + content

    return _store_object(full, tinygit_dir)


def update_ref(commit_hash: str, tinygit_dir=".tinygit") -> None:
    headpath = os.path.join(tinygit_dir, "HEAD")
    with open(headpath) as head:
        content = head.read()

    branch = content.split(maxsplit=1)[1].strip()

    with open(os.path.join(tinygit_dir, branch), "w") as file:
        file.write(commit_hash)

    return


def commit(files: list[tuple[str, bytes]], message: str, tinygit_dir=".tinygit") -> str:
    tree_entries: list[tuple[str, str, str]] = []
    for filename, data in files:
        blob_hash = write_blob(data, tinygit_dir)
        tree_entries.append(("100644", filename, blob_hash))

    tree_hash = write_tree(tree_entries, tinygit_dir)

    parent_hash = None
    headpath = os.path.join(tinygit_dir, "HEAD")
    if os.path.exists(headpath):
        with open(headpath) as head:
            content = head.read().strip()

        if content.startswith("ref:"):
            ref_path = os.path.join(tinygit_dir, content.split(maxsplit=1)[1].strip())
            if os.path.exists(ref_path):
                with open(ref_path) as ref:
                    parent_hash = ref.read().strip() or None

    commit_hash = write_commit(
        tree_hash=tree_hash,
        message=message,
        parent_hash=parent_hash,
        tinygit_dir=tinygit_dir,
    )

    update_ref(commit_hash, tinygit_dir)

    return commit_hash
