from typing import NamedTuple
import re
import sys
# import webCrawling

# Token Type & Regular expression

# | Token Type
# | >> empty-tag
# | >> balanced-tag
# | >> custom-tag
# | >> opening-tag-start
# | >> closing-tag-start
# | >> tag-end
# | >> attr-name
# | >> attr-value
# | >> text-node

# | Tag
# |     1. empty-tag
# |         matched with specific tag name
# |         : "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "track", "wbr"
# |
# |     2. balanced-tag
# |         matched with specific tag name
# |         : enrolled tags except empty-tag-name
# |         : "html","head","style","title","body","address","article","aside","footer","header","h1","h2","h3","h4","h5","h6","main","nav","section","blockquote","dd","div","dl","dt","figcaption","figure","li","menu","ol","p","pre","ul","a","abbr","b","bdo","cite","code","data","dfn","em","i","kbd","mark","q","rp","rt","ruby","s","samp","small","span","strong","sub","sup","time","u","var","audio","map","video","iframe","object","canvas","noscript","script","del","ins","caption","colgroup","table","tbody","td","tfoot","th","thead","tr","button","datalist","fieldset","form","label","legend","meter","optgroup","option","output","progress","select","textarea","details","dialog","summary","slot","template"
# |
# |     3. custom-tag
# |         regex : [a-z][a-z0-9-]*
# |         - start with lowercase
# |         - consist of lowercase, uppercase, digits, and -
# | 
# | Tag-Separator
# |     1. opening-tag-start
# |         : <
# |     2. closing-tag-start
# |         : </
# |     3. tag-end
# |         : >
# |
# |     4. empty-tag-end (deprecated) 
# |         : />
# |         selenium bot's html empty tag does not contain /> just >
# |         
# | Attributes
# |     regex : [a-z_][a-zA-Z0-9_-]+(="[^<>]*?")*
# |     - attr-name only or attr-name="attr-value"
# | 
# |         1. attr-name:
# |             regex : [a-z_][a-zA-Z0-9_-]+
# |             - should start lowercase or _
# |             - consist of lowercase, uppercase, digits, - and _
# |
# |         2. attr-value:
# |             regex : "[^<>]*?"
# |             - can be empty string ""
# |             - any string except < and >
# | 
# | Arguments
# |     1. text-node
# |         : appears between opening tag and closing tag
# | 

# | cf)
# | 
# | 1. opening Tag
# |     regex : <[a-z][a-z0-9-]*( [a-z_][a-zA-Z0-9_-]+(="[^<>]*")*)*>
# |     - should divide empty-tag and balanced-tag with saved tag name
# |
# | 2. closing Tag
# |     regex : <\/[a-z][a-z0-9-]*>

# Token Table Form

# | Token (type, name, name_no, total_no, tag_ref, attr_ref)
# |     count >> distinguish same tags
# |         attribute's count = None
# |     tag_no >> match tag and attributes
# |         if tag and attribute have same tag_no, then that attribute is tag's attribute
# |     attr_no >> match attr-name and attr-value
# |         Token_Type : tag's attr_no = None

class Token(NamedTuple):
    type: str # 토큰 타입
    name: str # 토큰 이름
    name_no: int # 중복된 토큰 이름 count
    total_no: int # 토큰 번호 
    tag_ref: int # 종속된 tag 토큰 번호 
    attr_ref: int # 종속된 attribute 토큰 번호
    
html = open("processed_html.txt", 'r').read()
tokenized_html = open("tokenized_html.txt", 'w')

# 공백, 줄바꿈, 탭 제거
# html = re.sub("    ", "", webCrawling.html)
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

# test - txt & html file
processed_html = open("processed_html.txt", 'w')
Formatted_html = open("processed_html.html", 'w')

processed_html.write(html)
Formatted_html.write(html)

processed_html.close()
Formatted_html.close()

empty_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "track", "wbr"]
balanced_tags = ["html","head","style","title","body","address","article","aside","footer","header","h1","h2","h3","h4","h5","h6","main","nav","section","blockquote","dd","div","dl","dt","figcaption","figure","li","menu","ol","p","pre","ul","a","abbr","b","bdo","cite","code","data","dfn","em","i","kbd","mark","q","rp","rt","ruby","s","samp","small","span","strong","sub","sup","time","u","var","audio","map","video","iframe","object","canvas","noscript","script","del","ins","caption","colgroup","table","tbody","td","tfoot","th","thead","tr","button","datalist","fieldset","form","label","legend","meter","optgroup","option","output","progress","select","textarea","details","dialog","summary","slot","template"]

total_tag_list = [] # 모든 tag를 list로 저장
non_empty_tag_stack = [] # non-empty tag를 stack으로 저장

tag_count = {} # tag 등장한 횟수 { link : 1 ...}

attr_name_list = [] # 모든 attribute name을 list로 저장
attr_names_only_list = [] # attribute name only만 list로 저장
attr_names_value_list = [] # attribute name=value를 list로 저장

# total stack
token_table = [] # 튜플 형태로 등장한 토큰 저장 (Token_Type, value, count, tag_no, attr_no)

while True:
    opening_tag = re.match('<[a-z][a-z0-9-]*([ a-z_][a-zA-Z0-9_-]+(="[^<>]*")*)*>', html)
    closing_tag = re.match('<\/[a-z][a-z0-9-]*>', html)
    text_node = re.match('[^<]*[^<>]+[^<>]*', html)
    
    if opening_tag:
        opening_tag = opening_tag.group(0)
        isAttributeExist = False # Attribute 여부 기본 설정
        
        tag = re.sub("<", "", opening_tag) # < 제거
        tag = re.sub(">", "", tag) # > 제거
        
        # Attribute 여부 확인 & tag name 추출
        if opening_tag.find(" ") != -1: # 공백 존재 여부 확인
            tag_name = tag[:tag.find(" ")] # tag name 추출
            isAttributeExist = True
        else:
            tag_name = tag
        
        # Tag name 별 token type 구분 및 stack 저장 
        total_tag_list.append(tag_name)
        
        if tag_name in empty_tags:
            token_type = "empty-tag"
        elif tag_name in balanced_tags:
            token_type = "balanced-tag"
        else:
            token_type = "custom-tag"
        
        # tag_count dictionary에 태그별 횟 수 저장
        # { html : 1, div : 56, .... }
        if tag_name in tag_count.keys():
            tag_count[tag_name] += 1 # 이미 존재하면 count + 1
        else:
            tag_count[tag_name] = 1  # 존재하지 않으면 count = 1
         
        # Token 생성, Token_table에 추가, 새 html에 작성
        opening_token = Token("opening-tag-start", "<", None, len(token_table), None, None)
        token_table.append(opening_token)
        tokenized_html.write("<opening-tag-start, %s, %d>\n" % ("<", len(token_table)))
        
        token = Token(token_type, tag_name, tag_count[tag_name], len(token_table), None, None)
        token_table.append(token)
        tokenized_html.write("<%s, %s, %d>\n" % (token_type, tag_name, len(token_table)))
        
        non_empty_tag_stack.append(token)
        
        if isAttributeExist:
            attrIter = re.finditer('[a-z_][a-zA-Z0-9_-]+(="[^<>]*?")*', tag[tag.find(" ")+1:])
            attr_count = 0

            while True:
                try:
                    attr = attrIter.__next__().group()
                    attr_count += 1
                    if attr.find("=") != -1:
                        # attribute가 name=value 꼴이면
                        attr = attr.split("=")
                        attr[1] = re.sub("\"", "", attr[1])
                        
                        attr_name_token = Token("attr-name", attr[0], None, len(token_table), tag_count[tag_name], attr_count)
                        token_table.append(attr_name_token)
                        tokenized_html.write("<attr-name, %s, %d>\n" % (attr[0], len(token_table)))
                        
                        attr_value_token = Token("attr-value", attr[1], None, len(token_table), tag_count[tag_name], attr_count)
                        token_table.append(attr_value_token)
                        tokenized_html.write("<attr-value, %s, %d>\n" % (attr[1], len(token_table)))
                        
                    else:
                        # attribute가 name only 꼴이면
                        attr_name_token = Token("attr-name", attr, None, len(token_table), tag_count[tag_name], attr_count)
                        token_table.append(attr_name_token)
                        tokenized_html.write("<attr-name, %s, %d>\n" % (attr, len(token_table)))
                    
                except StopIteration:
                    break
        
        closing_token = Token("tag-end", ">", None, len(token_table), tag_count[tag_name], attr_count)
        token_table.append(closing_token) 
        tokenized_html.write("<tag-end, %s, %d>\n" % (">", len(token_table)))
        
        html = html[len(opening_tag):]
        print("opening : ", opening_tag)
        
    elif closing_tag:
        # 해당 정보를 새로운 txt에 token화 해서 작성하기
        html = html[len(closing_tag):]
        print("closing : ", closing_tag)
    elif text_node:
        text_node = text_node.group(0)
        # 해당 정보를 새로운 txt에 token화 해서 작성하기
        html = html[len(text_node):]
        print("text_node : ", text_node)
    else:
        print("Tokenizing ERROR")
        tokenized_html.write("\n-----------------\nTokeninzing ERROR\n-----------------")
        break
    
tokenized_html.close()