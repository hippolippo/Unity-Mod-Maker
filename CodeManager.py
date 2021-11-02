import functools
import operator


class CodeLine:

    def __init__(self, code, locked=False):
        self.code = code
        self.locked = locked

    def indent(self):
        self.code = "    " + self.code

    def __repr__(self):
        return "\"" + self.code + "\""

    def get_text(self):
        return self.code

    def update_contents(self, code):
        if not self.locked:
            self.code = code
            return "Success"
        else:
            return "Locked"

    def is_locked(self):
        return self.locked

    def get_prefix(self):
        return CodeBlock(code_lines=[self])

    def get_postfix(self):
        return CodeBlock(code_lines=[self])

    def get_contents(self):
        return CodeBlock(code_lines=[self])

    def to_code_block(self):
        return CodeBlock(code_lines=[self])

    def get_block_list(self):
        return [(self.code, self.is_locked(), self)]

    def get_code_lines(self):
        lines = [self]
        return lines

    def get_list(self):
        return [None]

    def default_indent(self):
        pass


class Delimiter(CodeLine):
    def __init__(self, code):
        self.code = code
        self.locked = True

    def update_contents(self, code):
        return "Delimiter"


class CodeBlock:

    def __init__(self, code_lines=[], delimiter="\n"):
        self.lines = code_lines.copy()
        self.delimiter = Delimiter(delimiter)

    def indent(self):
        if len(self.lines) < 1:
            return
        self.lines[0].indent()
        if len(self.lines) < 2:
            return
        if self.delimiter.get_text() == "\n":
            [line.indent() for line in self.lines[1:]]

    def __add__(self, other):
        return CodeBlock(self.lines + other.lines)

    def __lshift__(self, other):
        self.lines = other
        return self.lines

    def add_line(self, code_line, location=None):
        if location is None:
            self.lines.append(code_line)
        else:
            self.lines.insert(location, code_line)

    def remove_line(self, code_line=None, location=-1):
        if code_line is not None:
            self.lines.pop(self.lines.index(code_line))
        else:
            self.lines.pop(location)

    def get_text(self):
        return "".join([line.get_text() for line in self.get_code_lines()])

    def get_prefix(self):
        return self

    def get_postfix(self):
        return self

    def get_contents(self):
        return self

    def to_code_block(self):
        return self

    def get_block_list(self):
        return [(line.get_text(), line.is_locked(), line) for line in self.lines]

    def get_list(self):
        return self.lines

    def get_code_lines(self):
        lines = sum([[line, self.delimiter] for line in self.lines], [])[:-1]
        return lines

    def default_indent(self):
        pass


class CodeBlockWrapper:

    def __init__(self, prefix=CodeBlock(), postfix=CodeBlock(), contents=CodeBlock(), delimiter="\n", indented=None):
        if indented is None and delimiter == "\n":
            indented = True
        elif indented is None:
            indented = False
        self.indented = indented
        self.delimiter = Delimiter(delimiter)
        self.prefix = prefix
        self.postfix = postfix
        self.contents = contents

    def indent(self):
        self.prefix.indent()
        if self.delimiter.get_text() == "\n":
            self.contents.indent()
            self.postfix.indent()

    def get_prefix(self):
        return self.prefix

    def get_postfix(self):
        return self.postfix

    def get_contents(self):
        return self.contents

    def to_code_block(self):
        prefix = self.prefix.to_code_block()
        contents = self.contents.to_code_block()
        postfix = self.contents.to_code_block()
        return prefix + contents + postfix

    def get_text(self):
        return "".join([line.get_text() for line in self.get_code_lines()])

    def get_code_lines(self):
        lines = sum([self.prefix.get_code_lines(),
                     self.delimiter.get_code_lines(),
                     self.contents.get_code_lines(),
                     self.delimiter.get_code_lines(),
                     self.postfix.get_code_lines()], [])
        return lines

    def get_block_list(self):
        return [(self.prefix.get_text(), False, self.prefix),
                (self.contents.get_text(), False, self.contents),
                (self.postfix.get_text(), False, self.postfix)]

    def get_list(self):
        return [self.prefix, self.contents, self.postfix]

    def default_indent(self):
        self.prefix.default_indent()
        self.contents.default_indent()
        self.postfix.default_indent()
        if self.indented:
            self.contents.indent()


class LargeCodeBlockWrapper:

    def __init__(self, block_list=[], delimiter="\n"):
        self.delimiter = Delimiter(delimiter)
        self.block_list = block_list.copy()

    def insert_block_after(self, block, after_block=None, position=None):
        if after_block is not None:
            self.block_list.insert(self.block_list.index(after_block) + 1, block)
        elif position is None:
            self.block_list.append(block)
        else:
            self.block_list.insert(position + 1, block)

    def indent(self):
        if len(self.block_list) < 1:
            return
        self.block_list[0].indent()
        if len(self.block_list) < 2:
            return
        if self.delimiter.get_text() == "\n":
            [block.indent() for block in self.block_list[1:]]

    def insert_block_before(self, block, after_block=None, position=None):
        if after_block is not None:
            self.block_list.insert(self.block_list.index(after_block), block)
        elif position is None:
            self.block_list.insert(0, block)
        else:
            self.block_list.insert(position, block)

    def get_prefix(self):
        return self.block_list[0]

    def get_postfix(self):
        return self.block_list[-1]

    def get_contents(self):
        return LargeCodeBlockWrapper(block_list=self.block_list[1:-1])

    def to_code_block(self):
        output = CodeBlock()
        for block in self.block_list:
            block = block.to_code_block()
            output = output + block
        return output

    def get_text(self):
        return "".join([line.get_text() for line in self.get_code_lines()])

    def get_code_lines(self):
        lines = sum([block.get_code_lines() + [self.delimiter] for block
                    in self.block_list], [])[:-1]
        return lines

    def get_block_list(self):
        return [(block.get_text(), False, block) for block in self.block_list]

    def get_list(self):
        return self.block_list

    def default_indent(self):
        [block.default_indent() for block in self.block_list]
