from compiler import HTML

compiler = HTML("error_source.txt")

text_node1 = compiler.search(['span', 'class', '"summary_info ng-star-inserted"'])
res1 = compiler.getTextNode(text_node1).split('$')

text_node2 = compiler.search(['span', 'class', '"value ng-star-inserted"'])
res2 = compiler.getTextNode(text_node2).split('$')

text_node3 = compiler.search(['em', 'class', '"label"'])
res3 = compiler.getTextNode(text_node3).split('$')