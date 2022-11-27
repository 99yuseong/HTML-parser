from typing import NamedTuple
import re
import sys

class Token(NamedTuple):
    type: str # 토큰 타입
    value: str # 토큰 값
    t_no: int # 토큰 번호

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

def create_token(t_type, t_value, t_table, t_html=None):
    token = Token(t_type, t_value, len(t_table))                # 토큰 생성
    t_table.append(token)                                       # table에 토큰 추가
    if t_html:
        t_html.write("(%s, %d : %s)\n" % (t_type, len(t_table)-1, t_value))   # tokenized_html.txt에 작성

def tokenize(html_txt): # return token_table
    tokenized_html = open("tokenized_html.txt", 'w')
    tokenized_table = open("token_table.txt", 'w')
    
    token_table = []
    
    html = open(html_txt, 'r').read()
    html = preprocess(html)
    
    while True:
        if len(html) == 0:
            for token in token_table:
                tokenized_table.write(str(token))
                tokenized_table.write("\n")
            
            tokenized_html.close()
            tokenized_table.close()
            return token_table
        
        opening_tag = re.match('<[^/<>][^<>]*>', html)
        closing_tag = re.match('<\/[a-z][a-zA-Z0-9-]*>', html)
        text_node = re.match('[^<>"]+|[^<>"]*("[^"]*")+[^<>"]*', html)
        
        if opening_tag:
            opening_tag = opening_tag.group(0)
            
            # create token
            create_token("opening-tag", opening_tag, token_table, tokenized_html)
            
            html = html[len(opening_tag):]

        elif closing_tag:
            closing_tag = closing_tag.group(0)
            
            # create token
            create_token("closing-tag", closing_tag, token_table, tokenized_html)
            
            html = html[len(closing_tag):]
            
        elif text_node:
            text_node = text_node.group(0)
            
            # create token
            create_token("text-node", text_node, token_table, tokenized_html)
            
            html = html[len(text_node):]
            
        else:
            opening_tag_idx = re.search('<[^/<>][^<>]*>', html)
            closing_tag_idx = re.search('<\/[a-z][a-zA-Z0-9-]*>', html)
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
            print("    %s..." % html[:error_end_idx])
            print("    ^")
            print("    check tokenized_html.txt to the log details")
            print()
            exit(1)
        
def tokenize_opening_tag(opening_tag): # return token_table
    
    token_table = []
    
    pure_opening_tag = opening_tag  # 에러 처리시 출력할 태그
    error_idx = 0                   # 에러 처리시 위치 출력용 idx
    error_check = ""
    
    # tag name 체크
    tag_name = re.match('<[!a-z][a-zA-Z0-9-]*', opening_tag)
    if tag_name:
        tag_name = tag_name.group(0)[1:] # < 제거 후 tag_name 저장
    else:
        print("TokenError : '%s' tag name is not acceptable" % opening_tag)
    
    create_token("opening", "<", token_table)
    create_token("tag-name", tag_name, token_table)
    
    opening_tag = opening_tag[len(tag_name) + 1:] # < + tag_name 만큼 길이 지워주기
    error_idx += len(tag_name) + 1                 # < + tag_name 길이 만큼 idx 이동
    error_check += ("<, %s" % tag_name)
    
    while True:
        if opening_tag == ">" or opening_tag == "/>":
            create_token("closing", opening_tag, token_table)
            for token in token_table:
                return token_table
        
        attr_name = re.match(' [a-z_][a-zA-Z0-9_-]*', opening_tag)
        attr_equal = re.match('=', opening_tag)
        attr_value = re.match('\"[^<>]*?\"', opening_tag)
         
        if attr_name:
            attr_name = attr_name.group(0)[1:] # 앞 공백 제거 후 attr_name 추출
            
            # create token
            create_token("attr-name", attr_name, token_table)
            
            opening_tag = opening_tag[len(attr_name) + 1:] # 공백 1 추가
            error_idx += len(attr_name) + 1
            
            error_check += (", %s" % attr_name)
            
        elif attr_equal:
            attr_equal = attr_equal.group(0)
            
            # create token
            create_token("attr-equal", attr_equal, token_table)
            
            opening_tag = opening_tag[len(attr_equal):]
            error_idx += len(attr_equal)
            
            error_check += ", ="
            
        elif attr_value:
            attr_value = attr_value.group(0)
            
            attr_value = re.sub("\"", "", attr_value)
            
            # create token
            create_token("attr-value", attr_value, token_table)
            
            opening_tag = opening_tag[len(attr_value) + 2:] # 양쪽 따옴표 추가
            error_idx += len(attr_value) + 2 
            
            error_check += (", \"%s\"" % attr_value)
            
        else:
            print()
            print("TokenError : '%s' is not tokenizable" % opening_tag)
            print("    %s" % pure_opening_tag)
            print(('{:>%d}' % (error_idx + 5)).format('^'))
            print("    log :", error_check)
            print()
            
            exit(1)
    

# tokenize("default_html.txt")
# tokenize_opening_tag("<meta ht\"tp-equiv=\"Content-Style-Type\" asdfafs content=\"text/css\"/>")
