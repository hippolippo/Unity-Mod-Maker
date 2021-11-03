import CodeManager
import copy

undo_stack = []
redo_stack = []
MAX_UNDO_STACK_SIZE = 0

def undo():
    global undo_stack, redo_stack
    if len(undo_stack) == 0: return None
    redo_stack.append(undo_stack.pop(-1))
    return redo_stack[-1]

def redo():
    global undo_stack, redo_stack
    if len(redo_stack) == 0: return None
    undo_stack.append(redo_stack.pop(-1))
    return undo_stack[-1]

def log_action(mod, clear_redo):
    global undo_stack, redo_stack
    if clear_redo:
        redo_stack = []
    undo_stack.append(copy.deepcopy(mod))

def update(mod, code, clear_redo=True):
    log_action(mod, clear_redo)
    if len(undo_stack) > MAX_UNDO_STACK_SIZE and MAX_UNDO_STACK_SIZE != 0:
        undo_stack.pop(0)
        print("over")
    mod_code = mod.get_text()
    if mod_code == code:
        return
    front = 0
    # Increment front index until the text isn't the same or you hit the end of one of them
    while mod_code[:front] == code[:front] and front < min(len(mod_code), len(code)):
        front += 1
    front -= 1
    back = -1
    # Decrement the back index until the text isn't the same or you hit front
    while mod_code[back:] == code[back:] and front - min(len(mod_code), len(code)) < back + 1:
        back -= 1
    back += 1
    added = code[front:back]
    print(front,back)
    delete(mod.get_code_lines(), front, len(mod_code) + back - front)
    add(mod, front, added)
    return front + len(added)


def delete(mod, front, amount):
    return [delete_char(mod, front) for i in range(amount)]


def delete_char(code_lines, index):
    accumulator = 0
    i = -1
    while accumulator <= index:
        i += 1
        if i >= len(code_lines):
            return
        accumulator += len(code_lines[i].get_text())
    accumulator -= len(code_lines[i].get_text())
    sub_index = index - accumulator
    string = [char for char in code_lines[i].get_text()]
    if len(string) == 0:
        code_lines.pop(i)
        return delete_char(code_lines, index)
    string.pop(sub_index)
    string = "".join(string)
    result = code_lines[i].update_contents(string)
    if result == "Success":
        return "Success"
    if result == "Locked":
        return "Locked"
    if result == "Delimiter":
        # There should never be a delimiter on the edge so this shouldn't have an exception
        if code_lines[i - 1].is_locked() or code_lines[i + 1].is_locked():
            return "Locked"
        code_lines.pop(i)
        # delimiter is deleted so index i is actually the CodeLine on the right now
        return code_lines[i - 1].update_contents(code_lines[i - 1].get_text() + code_lines[i].get_text())
    return "Error"


def add(mod, front, text):
    return [add_char(mod, front + i[0], i[1]) for i in enumerate(text)]


def add_char(mod, index, char):
    code_lines = mod.get_code_lines()
    accumulator = 0
    i = -1
    while accumulator <= index:
        i += 1
        if i >= len(code_lines):
            return
        accumulator += len(code_lines[i].get_text())
    accumulator -= len(code_lines[i].get_text())
    sub_index = index - accumulator
    if sub_index != 0 and sub_index < len(code_lines[i].get_text()) - 1:
        string = [char for char in code_lines[i].get_text()]
        string.insert(sub_index, char)
        string = "".join(string)
        result = code_lines[i].update_contents(string)
        return result
    if sub_index == 0:
        if type(code_lines[i - 1]) is CodeManager.Delimiter and code_lines[i - 1].get_text() != "":
            string = [char for char in code_lines[i].get_text()]
            string.insert(sub_index, char)
            string = "".join(string)
            result = code_lines[i].update_contents(string)
            return result
        before = i - 1
        if type(code_lines[before]) is CodeManager.Delimiter:
            before -= 1
        if code_lines[before].is_locked():
            string = [char for char in code_lines[i].get_text()]
            string.insert(sub_index, char)
            string = "".join(string)
            result = code_lines[i].update_contents(string)
            return result
        string = [char for char in code_lines[before].get_text()]
        string.append(char)
        string = "".join(string)
        result = code_lines[before].update_contents(string)
        return result
    if type(code_lines[i + 1]) is CodeManager.Delimiter and code_lines[i + 1].get_text() != "":
        string = [char for char in code_lines[i].get_text()]
        string.insert(sub_index, char)
        string = "".join(string)
        result = code_lines[i].update_contents(string)
        return result
    after = i + 1
    if type(code_lines[after]) is CodeManager.Delimiter:
        after += 1
    if not code_lines[i].is_locked():
        string = [char for char in code_lines[i].get_text()]
        string.insert(sub_index, char)
        string = "".join(string)
        result = code_lines[i].update_contents(string)
        return result
    else:
        string = [char for char in code_lines[after].get_text()]
        string.insert(0, char)
        string = "".join(string)
        result = code_lines[after].update_contents(string)
        return result
    return "Error"
