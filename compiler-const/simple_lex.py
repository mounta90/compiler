"""
python simple_lex.py mg.f23
"""

import sys

from ply.lex import lex


reserved = {
    "do": "K_DO",
    "double": "K_DOUBLE",
    "else": "K_ELSE",
    "exit": "K_EXIT",
    "function": "K_FUNCTION",
    "if": "K_IF",
    "integer": "K_INTEGER",
    "print_double": "K_PRINT_DOUBLE",
    "print_integer": "K_PRINT_INTEGER",
    "print_string": "K_PRINT_STRING",
    "procedure": "K_PROCEDURE",
    "program": "K_PROGRAM",
    "read_double": "K_READ_DOUBLE",
    "read_integer": "K_READ_INTEGER",
    "read_string": "K_READ_STRING",
    "return": "K_RETURN",
    "string": "K_STRING",
    "then": "K_THEN",
    "while": "K_WHILE",
}

# List of token names.   This is always required
tokens = [
    "ASSIGN",  # done
    "ASSIGN_PLUS",  # done
    "ASSIGN_MINUS",  # done
    "ASSIGN_MULTIPLY",  # done
    "ASSIGN_DIVIDE",  # done
    "ASSIGN_MOD",  # done
    "COMMA",  # done
    "COMMENT",  # done
    "DAND",  # done
    "DIVIDE",  # done
    "DOR",  # done
    "DEQ",  # done
    "GEQ",  # done
    "GT",  # done
    "LBRACKET",  # done
    "LEQ",  # done
    "LCURLY",  # done
    "LPAREN",  # done
    "LT",  # done
    "MINUS",  # done
    "DECREMENT",  # done
    "MOD",  # done
    "MULTIPLY",  # done
    "NE",  # done
    "NOT",  # done
    "PERIOD",  # done
    "PLUS",  # done
    "INCREMENT",  # done
    "RBRACKET",  # done
    "RCURLY",  # done
    "RPAREN",  # done
    "SEMI",  # done
    "SCONSTANT",  # done
    "ICONSTANT",  # done
    "DCONSTANT",  # done
    "IDENTIFIER",  # done
] + list(reserved.values())


# Regular expression rules for simple tokens
t_ASSIGN = r":="
t_ASSIGN_PLUS = r"\+="
t_ASSIGN_MINUS = r"\-="
t_ASSIGN_MULTIPLY = r"\*="
t_ASSIGN_DIVIDE = r"/="
t_ASSIGN_MOD = r"%="
t_COMMA = r","
t_ignore_COMMENT = r"//.*"
t_DAND = r"&&"
t_DIVIDE = r"/"
t_DOR = r"\|\|"
t_DEQ = r"=="
t_GEQ = r">="
t_GT = r">"
t_LBRACKET = r"\["
t_LEQ = r"<="
t_LCURLY = r"{"
t_LPAREN = r"\("
t_LT = r"<"
t_MINUS = r"-"
t_DECREMENT = r"--"
t_MOD = "%"
t_MULTIPLY = r"\*"
t_NE = r"!="
t_NOT = r"!"
t_PERIOD = r"."
t_PLUS = r"\+"
t_INCREMENT = t_PLUS + t_PLUS
t_RBRACKET = r"\]"
t_RCURLY = r"\}"
t_RPAREN = r"\)"
t_SEMI = r"\;"
t_SCONSTANT = r'"([^"]*)"'
t_ICONSTANT = r"[0-9]+"
t_DCONSTANT = r"([0-9]+\.[0-9]*|\.[0-9]+)(d[\-\+]?[0-9]*)?"


def t_IDENTIFIER(t):
    r"[a-zA-Z_\$][a-zA-Z_\$0-9]{0,30}"
    t.type = reserved.get(t.value, "IDENTIFIER")  # Check for reserved words
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex()

# Test it out
# data = open(sys.argv[1], "r").read()
data = "a := 34"

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    # print(tok)
    # print(tok.type, tok.value, tok.lineno, tok.lexpos)
