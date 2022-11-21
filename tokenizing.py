import re
import sys
import webCrawling

# {type, value, lineno, lexpos}

processed_html = open("processed_html.txt", 'w')

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
html = re.sub('style=".*?"', "", html)

processed_html.write(html)

# pure_html.close()
processed_html.close()