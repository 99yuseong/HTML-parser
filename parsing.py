from typing import NamedTuple

void_element =  [
    'area', 
    'base', 
    'br', 
    'col', 
    'command', 
    'embed', 
    'hr', 
    'img', 
    'input', 
    'keygen', 
    'link', 
    'meta', 
    'param', 
    'source', 
    'track', 
    'wbr'
]

class Token(NamedTuple):
    type: str # 토큰 타입
    value: str # 토큰 값
    t_no: int # 토큰 번호

def create_token(t_type, t_value, t_table, t_html=None):
    token = Token(t_type, t_value, len(t_table))                # 토큰 생성
    t_table.append(token)                                       # table에 토큰 추가
    if t_html:
        t_html.write("(%s, %d : %s)\n" % (t_type, len(t_table)-1, t_value))   # tokenized_html.txt에 작성

class Node:
    def __init__(self, data, children = []):
        self.data = data
        self.par = None
        self.children = []
        for child in children:
            child.par = self
            self.children.append(child)
    
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)

class Tag:
    parsing_table = (
        {"/":"S4", "=":None, "variable":"S14","value":None, ">":None, "S":"S1", "E":"S2", "T":"S6", "A":None, "B":None, "C":None},
        {"/":None, "=":None, "variable":None, "value":None, ">":"R0", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"S3", "=":None, "variable":None, "value":None, ">":"R1", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":None, "=":None, "variable":None, "value":None, ">":"R2", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":None, "=":None, "variable":"S14","value":None, ">":None, "S":None, "E":None, "T":"S5", "A":None, "B":None, "C":None},
        {"/":None, "=":None, "variable":None, "value":None, ">":"R3", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R4", "=":None, "variable":"S13","value":None, ">":"R4", "S":None, "E":None, "T":None, "A":"S7", "B":"S9", "C":"S10"},
        {"/":"R5", "=":None, "variable":"S13","value":None, ">":"R5", "S":None, "E":None, "T":None, "A":None, "B":"S8", "C":"S10"},
        {"/":"R6", "=":None, "variable":"R6", "value":None, ">":"R6", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R7", "=":None, "variable":"R7", "value":None, ">":"R7", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R8", "=":"S11","variable":"R8", "value":None, ">":"R8", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":None, "=":None, "variable":None, "value":"S12",">":None, "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R9", "=":None, "variable":"R9", "value":None, ">":"R9", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R10","=":"R10","variable":"R10","value":None, ">":"R10","S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
        {"/":"R11","=":None, "variable":"R11","value":None, ">":"R11","S":None, "E":None, "T":None, "A":None, "B":None, "C":None}
    )

    reduce_rule = (
        ['end','S'],
        ['S', 'E'],
        ['S', 'E', '/'],
        ['S', '/', 'T'],
        ['E', 'T'],
        ['E', 'T', 'A'],
        ['A', 'A', 'B'],
        ['A', 'B'],
        ['B', 'C'],
        ['B', 'C', '=', 'value'],
        ['C', 'variable'],
        ['T', 'variable']
    )

    def __init__(self, tag):
        self.tag = tag
        self.tag_name = None
        self.tag_type = None
        self.attribute = []
        self.token_table = []
        self.token_table_pos = []
        self.parse_tree = None
        self.parsing()

    def parsing(self):
        if not self.tokenize():
            return False
        if self.token_table[0].value != '<':
            return False
        stack = [0]
        symbols = []
        idx = 1
        while True:
            print('stack is', stack,'\nsymbols is', symbols, '\n')
            t, v, _ = self.token_table[idx]
            sym = v if t == 'symbol' else t
            rule = self.parsing_table[stack[-1]][sym]
            if not rule:
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
        opening_tag = self.tag
        error_check = ""
        
        tmp = ""
        character = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-:'

        for idx, char in enumerate(opening_tag):
            if tmp and tmp[0] == '"':
                tmp += char
                if char == '"':
                    create_token("value", tmp, self.token_table)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
            elif char in character:
                if not tmp: self.token_table_pos.append(idx)
                tmp += char
            elif char in '!<>=/':
                if tmp:
                    create_token("variable", tmp, self.token_table)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
                create_token("symbol", char, self.token_table)
                self.token_table_pos.append(idx)
                if error_check: error_check += ', '
                error_check += char
            elif char == ' ':
                if tmp:
                    create_token("variable", tmp, self.token_table)
                    if error_check: error_check += ', '
                    error_check += tmp
                    tmp = ""
            elif not tmp and char == '"':
                self.token_table_pos.append(idx)
                tmp += char
            else:
                print()
                print("TokenError : '%s' is not tokenizable" % opening_tag)
                print("    %s" % self.tag)
                print(('{:>%d}' % (idx + 5)).format('^'))
                print("    log :", error_check)
                print()
                return False
        return True

    def check_parse_tree(self, node):
        pass