from ParsingRule import ParsingRule
from Token import Token

class Node:
    def __init__(self, data = None, children = []):
        self.data = data
        self.par = None
        self.children = []
        for child in children:
            self.insert(child)
    
    def insert(self, node):
        node.par = self
        self.children.append(node)

    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)

class Element:
    def __init__(self, data, type = None):
        self.data = data
        self.type = type

    def __str__(self):
        return str(self.data) + ' ' + self.type
    
    def __repr__(self):
        return repr(self.data) + ' ' + self.type

class TextNode(Element):
    def __init__(self, data):
        super().__init__(data,'text_node')

class Tag(Element):
    def __init__(self, data):
        super().__init__(data)
        self.name = None
        self.attribute = []
        self.token_table = []
        self.token_table_pos = []
        self.parse_tree = None
        self.rule = ParsingRule()
        self.void_elements = self.rule.get_void_element()
        self.parsing_table = self.rule.get_parse_table()
        self.reduce_rule = self.rule.get_reduce_rule()
        self.error_rule = self.rule.get_error_rule()
        if self.parsing():
            self.check_parse_tree(self.parse_tree)
            if self.name in self.void_elements:
                if self.type != 'closing_tag':
                    self.type = 'empty_tag'
                    
    def create_token(self, t_type, t_value):
        token = Token(t_type, t_value, len(self.token_table))                # 토큰 생성
        self.token_table.append(token)                                       # table에 토큰 추가

    def parsing(self):
        if not self.tokenize():
            return False
        if self.token_table[0].value != '<':
            return False
        stack = [0]
        symbols = []
        idx = 1
        while True:
            # print('stack is', stack,'\nsymbols is', symbols, '\n')
            t, v, _ = self.token_table[idx]
            sym = v if t == 'symbol' else t
            rule = self.parsing_table[stack[-1]][sym]
            if not rule:
                print()
                print("Syntax Error : '%s' is not tokenizable" % self.data)
                print("    %s" % self.data)
                print(('{:>%d}' % (self.token_table_pos[idx] + 5)).format('^'))
                print()
                return False
            elif rule[0] == 'E':
                print()
                print(self.error_rule[int(rule[1:])])
                print("    %s" % self.data)
                print(('{:>%d}' % (self.token_table_pos[idx] + 5)).format('^'))
                print()
                return False
            elif rule == 'R0':
                self.parse_tree = symbols[-1]
                break
            elif rule[0] == 'S':
                stack.append(int(rule[1:]))
                symbols.append(Node(self.token_table[idx]))
                idx += 1
            elif rule[0] == 'R':
                reduce_rule = self.reduce_rule[int(rule[1:])]
                l = len(reduce_rule) - 1
                children = []
                for _ in range(l):
                    stack.pop()
                    children.append(symbols[-1])
                    symbols.pop()
                new_symbol = reduce_rule[0]
                new_rule = self.parsing_table[stack[-1]][new_symbol]
                stack.append(int(new_rule[1:]))
                symbols.append(Node(new_symbol,children[::-1]))
        return True

    def tokenize(self):
        opening_tag = self.data
        error_check = ""
        
        tmp = ""
        character = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-:'

        for idx, char in enumerate(opening_tag):
            if tmp and tmp[0] == '"':
                tmp += char
                if char == '"':
                    self.create_token("value", tmp)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
            elif char in character:
                if not tmp: self.token_table_pos.append(idx)
                tmp += char
            elif char in '!<>=/':
                if tmp:
                    self.create_token("variable", tmp)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
                self.create_token("symbol", char)
                self.token_table_pos.append(idx)
                if error_check: error_check += ', '
                error_check += char
            elif char == ' ':
                if tmp:
                    self.create_token("variable", tmp)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
            elif not tmp and char == '"':
                self.token_table_pos.append(idx)
                tmp += char
            else:
                print()
                print("TokenError : '%s' is not tokenizable" % opening_tag)
                print("    %s" % self.data)
                print(('{:>%d}' % (idx + 5)).format('^'))
                print("    log :", error_check)
                print()
                return False
        return True

    def check_parse_tree(self, node):
        tmp = []
        for child in node.children:
            tmp.append(self.check_parse_tree(child))
        if node.data == 'T':
            self.name = tmp[0]
        elif node.data == 'B':
            if len(tmp) == 1:
                self.attribute.append(tmp)
            else:
                self.attribute.append([tmp[0], tmp[-1]])
        elif node.data == 'C':
            return tmp[0]
        elif node.data == 'S':
            if len(tmp) == 1:
                self.type = "opening_tag"
            elif tmp[0] == 'E':
                self.type = "empty_tag"
            else:
                self.type = "closing_tag"
        if type(node.data) == Token:
            return node.data.value
        return node.data
    
    def check_attr(self, name, value):
        for li in self.attribute:
            if len(li) == 1:
                continue
            if li[0] == name and li[1] == value:
                return True
        return False

