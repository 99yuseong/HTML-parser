import re
import sys
import webCrawling

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
# |     regex : [a-z_][a-zA-Z0-9_-]+(="[^<>]*")*
# |     - attr-name only or attr-name="attr-value"
# | 
# |         1. attr-name:
# |             regex : [a-z_][a-zA-Z0-9_-]+
# |             - should start lowercase or _
# |             - consist of lowercase, uppercase, digits, - and _
# |
# |         2. attr-value:
# |             regex : "[^<>]*"
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


# | Table Form
# | (Token_Type, count, value, valid)

empty_tags = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "track", "wbr"]
balanced_tags = ["html","head","style","title","body","address","article","aside","footer","header","h1","h2","h3","h4","h5","h6","main","nav","section","blockquote","dd","div","dl","dt","figcaption","figure","li","menu","ol","p","pre","ul","a","abbr","b","bdo","cite","code","data","dfn","em","i","kbd","mark","q","rp","rt","ruby","s","samp","small","span","strong","sub","sup","time","u","var","audio","map","video","iframe","object","canvas","noscript","script","del","ins","caption","colgroup","table","tbody","td","tfoot","th","thead","tr","button","datalist","fieldset","form","label","legend","meter","optgroup","option","output","progress","select","textarea","details","dialog","summary","slot","template"]
custom_tags = []

# 공백, 줄바꿈, 탭 제거
html = re.sub("    ", "", webCrawling.html)
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


