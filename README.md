# No-more-Late

## Usage

```bash
  $ python tokenizing.py
```

## Token

```python
class Token(NamedTuple):
    type: str # 토큰 타입
    value: str # 토큰 값
    t_no: int # 토큰 번호
```

## Token type

```python
# base-tokenizing
| opening-tag
| closing-tag
| text-node

# opening-tag-tokenizing
| opening
| tag-name
| attr-name
| attr-equal
| attr-value
| closing
```

## Detail

```python
Tag
1. empty-tag
    matched with specific tag name
    : "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "track", "wbr"

2. balanced-tag
    matched with specific tag name
    : enrolled tags except empty-tag-name
    : "html","head","style","title","body","address","article","aside","footer","header","h1","h2","h3","h4","h5","h6","main","nav","section","blockquote","dd","div","dl","dt","figcaption","figure","li","menu","ol","p","pre","ul","a","abbr","b","bdo","cite","code","data","dfn","em","i","kbd","mark","q","rp","rt","ruby","s","samp","small","span","strong","sub","sup","time","u","var","audio","map","video","iframe","object","canvas","noscript","script","del","ins","caption","colgroup","table","tbody","td","tfoot","th","thead","tr","button","datalist","fieldset","form","label","legend","meter","optgroup","option","output","progress","select","textarea","details","dialog","summary","slot","template"

3. custom-tag
    regex : [a-z][a-z0-9-]*
    - start with lowercase
    - consist of lowercase, uppercase, digits, and -

Tag-Separator
1. opening-tag-start
    : <
2. closing-tag-start
    : </
3. tag-end
    : >

Attributes
regex : [a-z_][a-zA-Z0-9_-]+(="[^<>]*?")*
- attr-name only or attr-name="attr-value"

1. attr-name:
    regex : [a-z_][a-zA-Z0-9_-]+
    - should start lowercase or _
    - consist of lowercase, uppercase, digits, - and _
2. attr-value:
    regex : "[^<>]*?"
    - can be empty string ""
    - any string except < and >

Arguments
1. text-node
    regex : [^<]*[^<>]+[^<>]*
    : appears between opening tag and closing tag

cf)
1. opening Tag
    regex : <[!a-z][a-zA-Z0-9-]*([ a-z_][a-zA-Z0-9_-]+(="[^<>]*")*)*>
    - should divide empty-tag and balanced-tag with saved tag name

2. closing Tag
    regex : <\/[a-z][a-z0-9-]*>
```
