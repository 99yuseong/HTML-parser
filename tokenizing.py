from typing import NamedTuple
import re
import sys
# import webCrawling

    # <
    # >
    # </
    # tag hidden A="B"  >> text_node tag hidden A="B"
    # tag
    # hidden
    # A
    # =
    # "B"
    
    # <>
    # </>
    # text-node
    
    # </head attr = "">
    
    # <>
    # </aasdfasdfasdfasdf>
    # <meta sdlkfj="" />
    
    # <>
    # </>
    # <>
    # <"><">
    # >> <>
    
    # 1. 큰 따옴표가 잘 닫겼나
    # 2. 꺽쇠가 있냐없냐
    # 3. 근데 따옴표안에 있냐 없냐
    
    
    # <> -> token -> parsing
    
    # 1. <>로 감싸져 있는 것들
    # 2. </>로 감싸져 있는 것들
    # 3. 1,2를 제외한 <, >가 포함되지 않은 모든 문자열, 단 ""사이에 <,>가 들어간 것은 가능, ""가 홀수개이면 안됨

class Token(NamedTuple):
    type: str # 토큰 타입
    value: str # 토큰 값
    t_no: int # 토큰 번호
    
tokenized_html = open("tokenized_html.txt", 'w')
tokenized_table = open("token_table.txt", 'w')

test_simple_html = open('test.txt', 'r').read()
test_pure_html = open('default_html.txt', 'r').read()

def preprocess(html):    
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

def create_token(t_type, t_value, t_table, t_html):
    token = Token(t_type, t_value, len(t_table))
    t_table.append(token)
    t_html.write("<%s, %s, %d>\n" % (t_type, t_value, len(t_table)-1))

def tokenize(html_txt, result_txt):
    tokenized_html = open("tokenized_html.txt", 'w')
    tokenized_table = open("token_table.txt", 'w')
    
    token_table = []
    
    html = open(html_txt, 'r').read()
    html = preprocess(html)
    
    while True:
        if len(html) == 0:
            print("Tokenize is Done!")
            exit(0)
        
        opening_tag = re.match('<[^/<>][^<>]*>', html)
        closing_tag = re.match('<\/[^<>]+>', html)
        text_node = re.match('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html)
        
        if opening_tag:
            opening_tag = opening_tag.group(0)
            
            # create token
            create_token("opening-tag", opening_tag, token_table, tokenized_html)
            
            print("opening : ", opening_tag)
            html = html[len(opening_tag):]

        elif closing_tag:
            closing_tag = closing_tag.group(0)
            
            # create token
            create_token("closing-tag", closing_tag, token_table, tokenized_html)
            
            print("closing : ", closing_tag)
            html = html[len(closing_tag):]
            
        elif text_node:
            text_node = text_node.group(0)
            
            # create token
            create_token("text-node", text_node, token_table, tokenized_html)
            
            print("text_node : ", text_node)
            html = html[len(text_node):]
            
        else:
            opening_tag_idx = re.search('<[^/<>][^<>]*>', html).span()[0]
            closing_tag_idx = re.search('<\/[^<>]+>', html).span()[0]
            text_node_idx = re.search('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html).span()[0]
            
            error_fin_idx = min(opening_tag_idx, closing_tag_idx, text_node_idx)
                
            print("TokenError : '%s' is not tokenizable" % html[:error_fin_idx])
            break
    
    tokenized_html.close()
    tokenized_table.close()
        
        
# def tokenize_opening_tag(opening_tag):

# print(preprocess(test))
# tokenize(preprocess(test_simple_html))
tokenize("default_html.txt", 1)

# empty_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "track", "wbr"]
# balanced_tags = ["html","head","style","title","body","address","article","aside","footer","header","h1","h2","h3","h4","h5","h6","main","nav","section","blockquote","dd","div","dl","dt","figcaption","figure","li","menu","ol","p","pre","ul","a","abbr","b","bdo","cite","code","data","dfn","em","i","kbd","mark","q","rp","rt","ruby","s","samp","small","span","strong","sub","sup","time","u","var","audio","map","video","iframe","object","canvas","noscript","script","del","ins","caption","colgroup","table","tbody","td","tfoot","th","thead","tr","button","datalist","fieldset","form","label","legend","meter","optgroup","option","output","progress","select","textarea","details","dialog","summary","slot","template"]

# tag_count = {} # tag 등장한 횟수 { link : 1 ...}
# token_table = [] # Token 형태로 등장한 토큰 저장 Token(type, name, name_no, total_no, tag_ref, attr_ref)

# while True:
#     if len(html) == 0:
#         for token in token_table:
#             tokenized_table.write(str(token))
#             tokenized_table.write("\n")
            
#         tokenized_html.close()
#         tokenized_table.close()
#         exit(0)
    
#     opening_tag = re.match('<[!a-z][a-zA-Z0-9-]*([ a-z_][a-zA-Z0-9_-]+(="[^<>]*")*)*>', html)
#     closing_tag = re.match('<\/[a-z][a-z0-9-]*>', html)
#     text_node = re.match('[^<]*[^<>]+', html)
    
#     if opening_tag:
#         opening_tag = opening_tag.group(0)
#         isAttributeExist = False # Attribute 여부 기본 설정
        
#         tag = re.sub("<", "", opening_tag) # < 제거
#         tag = re.sub(">", "", tag) # > 제거
        
#         # Attribute 여부 확인 & tag name 추출
#         if opening_tag.find(" ") != -1: # 공백 존재 여부 확인
#             tag_name = tag[:tag.find(" ")] # tag name 추출
#             isAttributeExist = True
#         else:
#             tag_name = tag
        
#         # Tag name 별 token type 구분        
#         if tag_name in empty_tags:
#             token_type = "empty-tag"
#         elif tag_name in balanced_tags:
#             token_type = "balanced-tag"
#         else:
#             token_type = "custom-tag"
        
#         # tag_count dictionary에 태그별 횟 수 저장
#         # { html : 1, div : 56, .... }
#         if tag_name in tag_count.keys():
#             tag_count[tag_name] += 1 # 이미 존재하면 count + 1
#         else:
#             tag_count[tag_name] = 1  # 존재하지 않으면 count = 1
         
#         # Token 생성, Token_table에 추가, 새 html에 작성
#         opening_token = Token("opening-tag-start", "<", None, len(token_table), None, None)
#         token_table.append(opening_token)
#         tokenized_html.write("<opening-tag-start, %s, %d>\n" % ("<", len(token_table)))
        
#         token = Token(token_type, tag_name, tag_count[tag_name], len(token_table), None, None)
#         token_table.append(token)
#         tokenized_html.write("<%s, %s, %d>\n" % (token_type, tag_name, len(token_table)))
        
#         if isAttributeExist:
#             attrIter = re.finditer('[a-z_][a-zA-Z0-9_-]+(="[^<>]*?")*', tag[tag.find(" ")+1:])
#             attr_count = 0

#             while True:
#                 try:
#                     attr = attrIter.__next__().group()
#                     attr_count += 1
#                     if attr.find("=") != -1:
#                         # attribute가 name=value 꼴이면
#                         attr = attr.split("=")
#                         attr[1] = re.sub("\"", "", attr[1])
                        
#                         attr_name_token = Token("attr-name", attr[0], None, len(token_table), tag_count[tag_name], attr_count)
#                         token_table.append(attr_name_token)
#                         tokenized_html.write("<attr-name, %s, %d>\n" % (attr[0], len(token_table)))
                        
#                         attr_value_token = Token("attr-value", attr[1], None, len(token_table), tag_count[tag_name], attr_count)
#                         token_table.append(attr_value_token)
#                         tokenized_html.write("<attr-value, %s, %d>\n" % (attr[1], len(token_table)))
                        
#                     else:
#                         # attribute가 name only 꼴이면
#                         attr_name_token = Token("attr-name", attr, None, len(token_table), tag_count[tag_name], attr_count)
#                         token_table.append(attr_name_token)
#                         tokenized_html.write("<attr-name, %s, %d>\n" % (attr, len(token_table)))
                    
#                 except StopIteration:
#                     break
        
#         closing_token = Token("tag-end", ">", None, len(token_table), None, None)
#         token_table.append(closing_token) 
#         tokenized_html.write("<tag-end, %s, %d>\n" % (">", len(token_table)))
        
#         html = html[len(opening_tag):]
#         # print("opening : ", opening_tag)
        
#     elif closing_tag:
#         closing_tag = closing_tag.group(0)
        
#         tag_name = re.sub("</", "", closing_tag) # </ 제거
#         tag_name = re.sub(">", "", tag_name) # > 제거
        
#         if tag_name in balanced_tags:
#             token_type = "balanced-tag"
#         else:
#             token_type = "custom-tag"
                
#         closing_start_token = Token("closing-tag-start", "</", None, len(token_table), None, None)
#         token_table.append(closing_start_token) 
#         tokenized_html.write("<closing-tag-start, %s, %d>\n" % ("</", len(token_table)))
        
#         closing_tag_token = Token(token_type, tag_name, None, len(token_table), None, None)
#         token_table.append(closing_tag_token) 
#         tokenized_html.write("<%s, %s, %d>\n" % (token_type, tag_name, len(token_table)))
        
#         closing_end_token = Token("tag-end", ">", None, len(token_table), None, None)
#         token_table.append(closing_end_token) 
#         tokenized_html.write("<tag-end, %s, %d>\n" % (">", len(token_table)))
        
#         html = html[len(closing_tag):]
#         # print("closing : ", closing_tag)
        
#     elif text_node:
#         text_node = text_node.group(0)
        
#         text_token = Token("text-node", text_node, None, len(token_table), None, None)
#         token_table.append(text_token) 
#         tokenized_html.write("<%s, %s, %d>\n" % ("text-node", text_node, len(token_table)))
        
#         html = html[len(text_node):]
#         # print("text_node : ", text_node)
#     else:
#         print("Tokenizing ERROR")
#         tokenized_html.write("\n-----------------\nTokeninzing ERROR\n-----------------")
#         break