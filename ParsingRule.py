class ParsingRule:
    def __init__(self):
        # Tag tokenizing
        self.void_elements = [
            'area', 
            'base', 
            'br', 
            'col', 
            'command', 
            'embed', 
            'hr', 
            'img', 
            'input', 
            'keygen', 
            'link', 
            'meta', 
            'param', 
            'source', 
            'track', 
            'wbr'
        ]
        
        # parsing
        self.parsing_table = (
            {"/":"S4", "=":"E0", "variable":"S14","value":"E0", ">":"E1", "S":"S1", "E":"S2", "T":"S6", "A":None, "B":None, "C":None},
            {"/":"E2", "=":"E3", "variable":"E4", "value":"E4", ">":"R0", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"S3", "=":"E5", "variable":None, "value":"E6", ">":"R1", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"E2", "=":"E3", "variable":"E4", "value":"E4", ">":"R2", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"E0", "=":"E0", "variable":"S14","value":"E0", ">":"E1", "S":None, "E":None, "T":"S5", "A":None, "B":None, "C":None},
            {"/":"E7", "=":"E7", "variable":"E8", "value":"E8", ">":"R3", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R4", "=":"E1", "variable":"S13","value":"E6", ">":"R4", "S":None, "E":None, "T":None, "A":"S7", "B":"S9", "C":"S10"},
            {"/":"R5", "=":"E5", "variable":"S13","value":"E6", ">":"R5", "S":None, "E":None, "T":None, "A":None, "B":"S8", "C":"S10"},
            {"/":"R6", "=":"E5", "variable":"R6", "value":"E6", ">":"R6", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R7", "=":"E5", "variable":"R7", "value":"E6", ">":"R7", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R8", "=":"S11","variable":"R8", "value":"E9", ">":"R8", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"E10","=":"E11","variable":"E10","value":"S12",">":"E10","S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R9", "=":"E5", "variable":"R9", "value":"E6", ">":"R9", "S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R10","=":"R10","variable":"R10","value":"E9", ">":"R10","S":None, "E":None, "T":None, "A":None, "B":None, "C":None},
            {"/":"R11","=":"E5", "variable":"R11","value":"E6", ">":"R11","S":None, "E":None, "T":None, "A":None, "B":None, "C":None}
        )
        
        self.reduce_rule = (
            ['end','S'],
            ['S', 'E'],
            ['S', 'E', '/'],
            ['S', '/', 'T'],
            ['E', 'T'],
            ['E', 'T', 'A'],
            ['A', 'A', 'B'],
            ['A', 'B'],
            ['B', 'C'],
            ['B', 'C', '=', 'value'],
            ['C', 'variable'],
            ['T', 'variable']
        )
        
        self.error_rule = (
            "Syntax Error : There should be tag name after '<' or '</'", # E0
            "Syntax Error : There is no tag name",   # E1
            "Syntax Error : Tag should end with only one '/'",  # E2
            "Syntax Error : Tag should be end '>' or '/>'", # E3
            "Syntax Error : Attribute can not exist after '/'", # E4
            "Syntax Error : There is no variable before '='",   # E5
            "Syntax Error : Attribute value can not used alone",    # E6
            "Syntax Error : Closing tag should end '>'", # E7
            "Syntax Error : Attribute can not exist in closing tag", # E8
            "Syntax Error : There should be '=' between attribute name and value",   # E9
            "Syntax Error : There should be attribute value after '='", # E10
            "Syntax Error : '==' is not defined symbol"   # E11
        )
    
    def get_void_element(self):
        return self.void_elements
    
    def get_parse_table(self):
        return self.parsing_table
    
    def get_reduce_rule(self):
        return self.reduce_rule
    
    def get_error_rule(self):
        return self.error_rule