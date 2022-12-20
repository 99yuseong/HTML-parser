from typing import NamedTuple

class Token(NamedTuple):
    type: str # 토큰 타입
    value: str # 토큰 값
    t_no: int # 토큰 번호