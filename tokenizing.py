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

# | Tuple (Token_Type, value, count, tag_no, attr_no)
# |     count >> distinguish same tags
# |         attribute's count = None
# |     tag_no >> match tag and attributes
# |         if tag and attribute have same tag_no, then that attribute is tag's attribute
# |     attr_no >> match attr-name and attr-value
# |         Token_Type : tag's attr_no = None

html = open("processed_html.txt", 'r').read()

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

empty_tag_count = {} # empty tag 등장한 횟수 { link : 1 ...}
balanced_tag_count = {} # balanced tag 등장한 횟수 { div : 60 ... }
custom_tag_count = {} # custom tag 등장한 횟수 { custom_tag : 1 ...}
 
attr_name_list = [] # 모든 attribute name을 list로 저장
attr_names_only_list = [] # attribute name only만 list로 저장
attr_names_value_list = [] # attribute name=value를 list로 저장

# total stack
token_table = [] # 튜플 형태로 등장한 토큰 저장 (Token_Type, value, count, tag_no, attr_no)

# 정규표현식에 여러 group이 존재해서 finditer로 이터레이터로 받아야함
openingsIter = re.finditer('<[a-z][a-z0-9-]*([ a-z_][a-zA-Z0-9_-]+(="[^<>]*")*)*>', html)
while True:
    try:
        # 각 opening tag 별로 < > 제거 후 tag name과 attribute 추출
        opening_tag = openingsIter.__next__().group()
        opening_tag = re.sub("<", "", opening_tag) # < 제거
        opening_tag = re.sub(">", "", opening_tag) # > 제거
        
        isAttributeExist = False
        
        if opening_tag.find(" ") != -1: # 공백 존재 여부로 attribute 존재 확인
            tag = opening_tag[:opening_tag.find(" ")] # tag name 추출
            isAttributeExist = True
        
        # tag name이 나온 횟수를 각각 empty_tag_list, non_empty_tag_list에 저장
        # ex) { html : 1, div : 5 ...}
        if tag in empty_tags:
            token_type = "empty-tag"
            count = empty_tag_count
            if tag in empty_tag_count.keys():
                empty_tag_count[tag] += 1 # 이미 존재하면 count + 1
            else:
                empty_tag_count[tag] = 1  # 존재하지 않으면 count = 1
        
        elif tag in balanced_tags:
            token_type = "balanced-tag"
            count = balanced_tag_count
            non_empty_tag_stack.append(tag) # 나중에 닫는 tag랑 연결시켜주기 위해 stack에 저장
            if tag in balanced_tag_count.keys():
                balanced_tag_count[tag] += 1
            else:
                balanced_tag_count[tag] = 1
        else:
            token_type = "balanced-tag"
            count = custom_tag_count
            non_empty_tag_stack.append(tag) # 나중에 닫는 tag랑 연결시켜주기 위해 stack에 저장
            if tag in custom_tag_count.keys():
                custom_tag_count[tag] += 1
            else:
                custom_tag_count[tag] = 1
        
        total_tag_list.append(tag)
        
        #(Token_Type, value, count, tag_no, attr_no)
        token_table.append( (token_type, tag, count[tag], len(total_tag_list),  None) )
  
        if isAttributeExist:
            # attribute 이터레이터 생성
            attrIter = re.finditer('[a-z_][a-zA-Z0-9_-]+(="[^<>]*?")*', opening_tag[opening_tag.find(" ")+1:])
            attr_count = 0
            while True:
                try:
                    attr = attrIter.__next__().group()
                    attr_count += 1
                    if attr.find("=") != -1:
                        # attribute가 name=value 꼴이면
                        attr = attr.split("=")
                        attr[1] = re.sub("\"", "", attr[1])

                        token_table.append(("attr-name", attr[0], None, len(total_tag_list), attr_count))
                        token_table.append(("attr-value", attr[1], None, len(total_tag_list), attr_count))
                    else:
                        # attribute가 name only 꼴이면
                        token_table.append(("attr-name", attr[0], None, len(total_tag_list), attr_count))
                    
                except StopIteration:
                    break
                
    except StopIteration:
        break

for token in token_table:
    print(token)

# 정규표현식이 단일 group이라 list로 받을 수 있음
closings = re.findall('<\/[a-z][a-z0-9-]*>',html)