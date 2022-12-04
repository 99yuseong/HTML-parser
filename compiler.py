from typing import NamedTuple
import re
import sys
from datetime import datetime

void_elements =  [
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

def printLog(input): # let log be printed with timestamp
    timestamp = datetime.now()
    log = f'[{timestamp}] {input}'
    print(log)


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

    def __init__(self, data):
        super().__init__(data)
        self.name = None
        self.attribute = []
        self.token_table = []
        self.token_table_pos = []
        self.parse_tree = None
        self.parsing()
        self.check_parse_tree(self.parse_tree)
        if self.name in void_elements:
            if self.type != 'closing_tag':
                self.type = 'empty_tag'

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

class HTML:
    def __init__(self, file_name = ""):
        self.tokenized = [] # Text_node, Tag
        self.dom_tree = Node(None)
        self.tokenize(file_name)
        printLog("Tokenizing Complete")
        self.DOM_parsing()
        
    def preprocess(self, html):    
        # 공백, 줄바꿈, 탭 제거
        html = re.sub("    ", "", html)
        html = re.sub("  ", "", html)
        html = re.sub("\n", "", html)
        html = re.sub("\t", "", html)

        # 주석 제거
        html = re.sub("<!--.*?-->", "", html)

        # script 제거
        html = re.sub('<script.*?>.*?<\/script>', '', html)

        # no-script 제거
        html = re.sub('<noscript.*?>.*?</noscript>', '', html)

        # style 제거
        html = re.sub('<style.*?>.*?</style>', '', html)
        html = re.sub(' style=".*?"', "", html)

        # event listener 제거
        html = re.sub(' onclick=".*?"', "", html)
        html = re.sub(' onerror=".*?"', "", html)
        html = re.sub(' onmouseover=".*?"', "", html)
        html = re.sub(' onmouseout=".*?"', "", html)
        html = re.sub(' onfocus=".*?"', "", html)
        html = re.sub(' onfocusout=".*?"', "", html)
        html = re.sub(' onblur=".*?"', "", html)
        html = re.sub(' onkeydown=".*?"', "", html)
        html = re.sub(' onkeyup=".*?"', "", html)
        
        return html
    
    def print_dom_parser(self, text_file, node = None, depth = 0):
        if node == None:
            node = self.dom_tree
            for nxtNode in node.children:
                self.print_dom_parser(text_file, nxtNode)
        else:
            tmp = "    " * depth + node.data.data + "\n"
            n = text_file.write(tmp)
            for nxtNode in node.children:
                self.print_dom_parser(text_file, nxtNode, depth + 1)
            if node.data.type == 'opening_tag':
                n = text_file.write("    " * depth + "</" + node.data.name + ">\n")

    def tokenize(self, html_txt): # return token_table
        tokenized_html = open("tokenized_html.txt", 'w', encoding='UTF-8')
        tokenized_table = open("token_table.txt", 'w',  encoding='UTF-8')
        
        html = open(html_txt, 'r', encoding='UTF-8').read()
        html = self.preprocess(html)
        
        while True:
            if len(html) == 0:
                for token in self.tokenized:
                    tokenized_table.write(str(token))
                    tokenized_table.write("\n")
                
                tokenized_html.close()
                tokenized_table.close()
                return self.tokenized
            
            opening_tag = re.match('<[^/<>][^<>]*>', html)
            closing_tag = re.match('<\/[a-z][a-zA-Z0-9-:]*>', html)
            text_node = re.match('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html)
            
            if opening_tag:
                opening_tag = opening_tag.group(0)
                
                # create token
                create_token("opening-tag", opening_tag, self.tokenized, tokenized_html)
                
                html = html[len(opening_tag):]

            elif closing_tag:
                closing_tag = closing_tag.group(0)
                
                # create token
                create_token("closing-tag", closing_tag, self.tokenized, tokenized_html)
                
                html = html[len(closing_tag):]
                
            elif text_node:
                text_node = text_node.group(0)
                
                # create token
                create_token("text-node", text_node, self.tokenized, tokenized_html)
                
                html = html[len(text_node):]
                
            else:
                opening_tag_idx = re.search('<[^/<>][^<>]*>', html)
                closing_tag_idx = re.search('<\/[a-z][a-zA-Z0-9-:]*>', html)
                text_node_idx = re.search('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html)
                
                opening_tag_start_idx = opening_tag_idx.span()[0] if opening_tag_idx else len(html)
                closing_tag_start_idx = closing_tag_idx.span()[0] if closing_tag_idx else len(html)
                text_node_start_idx = text_node_idx.span()[0] if text_node_idx else len(html)
                
                opening_tag_end_idx = opening_tag_idx.span()[1] if opening_tag_idx else len(html)
                closing_tag_end_idx = closing_tag_idx.span()[1] if closing_tag_idx else len(html)
                
                error_start_idx = min(opening_tag_start_idx, closing_tag_start_idx, text_node_start_idx)
                error_end_idx = min(opening_tag_end_idx, closing_tag_end_idx)
                
                tokenized_html.write("\nTokenError : '%s' is not tokenizable" % html[:error_start_idx])
                
                print()
                print("TokenError : '%s' is not tokenizable" % html[:error_start_idx])
                print("    %s…" % html[:error_end_idx])
                print("    ^")
                print("    check tokenized_html.txt to the log details")
                print()
                exit(1)
        
    def DOM_parsing(self):
        curNode = self.dom_tree
        for t, v, _ in self.tokenized:
            nxtData = TextNode(v) if t == 'text-node' else Tag(v)
            if nxtData.type == 'opening_tag':
                nxtNode = Node(nxtData)
                curNode.insert(nxtNode)
                curNode = nxtNode
            elif nxtData.type == 'closing_tag':
                if curNode.data.name != nxtData.name:
                    print("dom parser error")
                    return False
                curNode = curNode.par
            else:
                curNode.insert(Node(nxtData))
        return True
        
    def search(self, data, node = None): # data = [tag_name, attr_name, attr_value]
        ans = []
        if node == None:
            for nxtNode in self.dom_tree.children:
                ans += self.search(data, nxtNode)
        else:
            curData = node.data
            if curData.type == 'text_node':
                return []
            if curData.name == data[0] and curData.check_attr(data[1],data[2]):
                ans.append(node)
            for nxtNode in node.children:
                ans += self.search(data, nxtNode)
        return ans
    
    def getTextNode(self, node):
        ans = ""
        if type(node) == list:
            for nxtNode in node:
                ans += self.getTextNode(nxtNode)
        elif node == None:
            for nxtNode in self.dom_tree.children:
                ans += self.getTextNode(nxtNode)
        else:
            curData = node.data
            if curData.type == 'text_node':
                ans += curData.data
            for nxtNode in node.children:
                ans += '$' + self.getTextNode(nxtNode)
        return ans

