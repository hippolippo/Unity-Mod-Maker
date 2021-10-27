class Change:
    def __init__(self, category="add", index=0, contents="", amount=0):
        self.category = category
        self.index = index
        self.contents = contents
        self.amount = amount


def find_changes(old, new):
    i = 0
    while old[:i] == new[:i] :
        print(old[:i], new[:i])
        i += 1
    i -= 1
    j = -1
    while old[j:] == new[j:]:
        j -= 1
        print(old[j:], new[j:])
    j += 1
    print(old[j:], new[j:])
    old_end = len(old) + j
    new_end = len(new) + j
    start = i
    change = Change()
    print(i, old_end)
    if new_end == i and len(new) > len(old):
        change.category = "rem"
        print("rem")
    if len(old) < len(new):
        change.category = "add"
        change.contents = 1


def handle_key_event(oldstring, newstring, e):
    pass


if __name__ == "__main__":
    find_changes("hello world", "hello world")
