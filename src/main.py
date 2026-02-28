import os


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
