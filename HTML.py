from Node import Node, TextNode, Tag
from Token import Token
import re
from sys import exit, setrecursionlimit

class HTML:
    def __init__(self, file_name = ""):
        self.tokenized = [] # Text_node, Tag
        self.dom_tree = Node(None)
        self.tokenize(file_name)
        self.DOM_parsing()
        
    def create_token(self, t_type, t_value):
        token = Token(t_type, t_value, len(self.tokenized))                # 토큰 생성
        self.tokenized.append(token)                                       # table에 토큰 추가
        
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
    
    def print_dom_tree(self, file_name):
        setrecursionlimit(10**7)
        text_file = open(file_name, 'w', encoding='UTF-8')
        self.print_dom_elements(text_file)
        text_file.close()
    
    def print_dom_elements(self, text_file, node = None, depth = 0):
        if node == None:
            node = self.dom_tree
            for nxtNode in node.children:
                self.print_dom_elements(text_file, nxtNode)
        else:
            tmp = "    " * depth + node.data.data + "\n"
            n = text_file.write(tmp)
            for nxtNode in node.children:
                self.print_dom_elements(text_file, nxtNode, depth + 1)
            if node.data.type == 'opening_tag':
                n = text_file.write("    " * depth + "</" + node.data.name + ">\n")

    def tokenize(self, html_txt): # return token_table
        html = open(html_txt, 'r', encoding='UTF-8').read()
        html = self.preprocess(html)
        
        while True:
            if len(html) == 0:
                return self.tokenized
            
            opening_tag = re.match('<[^/<>][^<>]*>', html)
            closing_tag = re.match('<\/[a-z][a-zA-Z0-9-:]*>', html)
            text_node = re.match('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html)
            
            if opening_tag:
                opening_tag = opening_tag.group(0)
                
                # create token
                self.create_token("opening-tag", opening_tag)
                
                html = html[len(opening_tag):]

            elif closing_tag:
                closing_tag = closing_tag.group(0)
                
                # create token
                self.create_token("closing-tag", closing_tag)
                
                html = html[len(closing_tag):]
                
            elif text_node:
                text_node = text_node.group(0)
                
                # create token
                self.create_token("text-node", text_node)
                
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
                
                print()
                print("TokenError : '%s' is not tokenizable" % html[:error_start_idx])
                print("    %s…" % html[:error_end_idx])
                print("    ^")
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
    
    def search_all(self, data):
        return self.getTextNode(self.search(data)).split('$')[1:]
        
    def search(self, data, node = None): # data = [tag_name, attr_name, attr_value]
        ans = []
        if node == None:
            for nxtNode in self.dom_tree.children:
                ans += self.search(data, nxtNode)
        else:
            curData = node.data
            if curData.type == 'text_node':
                return []
            if curData.name == data[0] and curData.check_attr(data[1], '"' + data[2] + '"'):
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

