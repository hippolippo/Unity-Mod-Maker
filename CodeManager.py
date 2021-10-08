class CodeLine:

    def __init__(self, code):
        self.code = code

    def get_text(self):
        return self.code

    def get_lines(self):
        return [self]

    def get_prefix(self): return CodeBlock(code_lines=[self])
    def get_postfix(self): return CodeBlock(code_lines=[self])
    def get_contents(self): return CodeBlock(code_lines=[self])
    def to_code_block(self): return CodeBlock(code_lines=[self])
    def get_block_list(self): return [self.code]
    def get_list(self): return [None]


class CodeBlock:

    def __init__(self, code_lines=[], delimiter="\n"):
        self.lines = code_lines.copy()
        self.delimiter = delimiter

    def __add__(self, other):
        return CodeBlock(self.lines + other.lines)

    def __lshift__(self, other):
        self.lines = other
        return self.lines

    def get_text(self):
        return self.delimiter.join([line.get_text() for line in self.lines])

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

    def get_lines(self):
        return self.lines

    def get_prefix(self): return self
    def get_postfix(self): return self
    def get_contents(self): return self
    def to_code_block(self): return self
    def get_block_list(self): return [line.get_text() for line in self.lines]
    def get_list(self): return self.lines


class CodeBlockWrapper:

    def __init__(self, prefix=CodeBlock(), postfix=CodeBlock(), contents=CodeBlock(), delimiter="\n"):
        self.delimiter = delimiter
        self.prefix = prefix
        self.postfix = postfix
        self.contents = contents

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

    def get_lines(self):
        return self.to_code_block().get_lines()

    def get_text(self):
        return self.prefix.get_text() + self.delimiter + self.contents.get_text() + self.delimiter +\
               self.postfix.get_text()

    def get_block_list(self): return [self.prefix.get_text(), self.contents.get_text(), self.postfix.get_text()]
    def get_list(self): return [self.prefix, self.contents, self.postfix]


class LargeCodeBlockWrapper:

    def __init__(self, block_list=[], delimiter="\n"):
        self.delimiter = delimiter
        self.block_list = block_list.copy()

    def insert_block_after(self, block, after_block=None, position=None):
        if after_block is not None:
            self.block_list.insert(self.block_list.index(after_block)+1, block)
        elif position is None:
            self.block_list.append(block)
        else:
            self.block_list.insert(position + 1, block)

    def insert_block_before(self, block, after_block=None, position=None):
        if after_block is not None:
            self.block_list.insert(self.block_list.index(after_block), block)
        elif position is None:
            self.block_list.insert(0, block)
        else:
            self.block_list.insert(position, block)

    def get_prefix(self): return self.block_list[0]
    def get_postfix(self): return self.block_list[-1]
    def get_contents(self): return LargeCodeBlockWrapper(block_list=self.block_list[1:-1])

    def to_code_block(self):
        output = CodeBlock()
        for block in self.block_list:
            block = block.to_code_block()
            output = output + block
        return output

    def get_lines(self): return self.to_code_block().get_lines()

    def get_text(self): return self.delimiter.join([block.get_text() for block in self.block_list])
    def get_block_list(self): return [block.get_text() for block in self.block_list]
    def get_list(self): return self.block_list


