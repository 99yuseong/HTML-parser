import time
from compiler import HTML
from bs4 import BeautifulSoup


start_own = time.time()
com = HTML("source.txt")

text_node1 = com.search(['span', 'class', '"summary_info ng-star-inserted"'])
res1 = com.getTextNode(text_node1).split('$')

text_node2 = com.search(['span', 'class', '"value ng-star-inserted"'])
res2 = com.getTextNode(text_node2).split('$')

text_node3 = com.search(['em', 'class', '"label"'])
res3 = com.getTextNode(text_node3).split('$')

time_own_res = time.time() - start_own

# -----------------------------------------------------------------------------------

start_bs = time.time()

source = open("source.txt", 'r', encoding="UTF-8")
html = source.read()
source.close()

soup = BeautifulSoup(html, 'html.parser')

data1 = soup.find('span', {'class' : 'summary_info ng-star-inserted'}).get_text()
data2 = soup.find('span', {'class' : 'value ng-star-inserted'}).get_text()
data3 = soup.find('em', {'class' : 'label'}).get_text()

time_bs_res = time.time() - start_bs

print("runtime of our parser is", time_own_res)
print("runtime of bs4 library's parser is", time_bs_res)

