import time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from HTML import HTML
from bs4 import BeautifulSoup

start_own = time.time()
com = HTML("source.txt")

text_node1 = com.get_text_all(['span', 'class', 'summary_info ng-star-inserted'])
text_node2 = com.get_text_all(['span', 'class', 'value ng-star-inserted'])
text_node3 = com.get_text_all(['em', 'class', 'label'])

node = com.search_all(['em', 'class', 'label'])

time_own_res = time.time() - start_own

# -----------------------------------------------------------------------------------

start_bs = time.time()

source = open("source.txt", 'r', encoding="UTF-8")
html = source.read()
source.close()

soup = BeautifulSoup(html, 'html.parser')

data1 = [ data.get_text() for data in soup.find_all('span', {'class' : 'summary_info ng-star-inserted'})]
data2 = [ data.get_text() for data in soup.find_all('span', {'class' : 'value ng-star-inserted'})]
data3 = [ data.get_text() for data in soup.find_all('em', {'class' : 'label'})]

time_bs_res = time.time() - start_bs

print("runtime of our parser is", time_own_res)
print("runtime of bs4 library's parser is", time_bs_res)

