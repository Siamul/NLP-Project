def titleindex(filename="titles"):
    with open(filename, encoding="utf8") as fh:
        return fh.read().split("\n")

def loadplots(filename="plots"):
    with open(filename, encoding="utf8") as fh:
        return fh.read().split("<EOS>")
