from functools import wraps
import sys
import ply.yacc as yacc

from node_types import *
from simple_lex import tokens


class Node:
    def __init__(self, type, meta=None, children=None):
        self.type = type
        self.meta = meta
        if children is not None:
            if not isinstance(children, list):
                self.children = [children]
            else:
                self.children = children
        else:
            self.children = []

    def append_child(self, child: "Node"):
        self.children.append(child)

    @staticmethod
    def print_tree(node):
        print()
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~ WALKING THROUGH THE PARSE TREE ~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print()

        level = "1"
        print(
            "Position: {: >15} | Parent Position: {: >15} |".format(level, "N/A"), node
        )
        queue = [
            (child, "{}{}".format(level, position), level)
            for position, child in enumerate(node.children)
        ]
        while queue:
            node, position, parent = queue.pop(0)
            print(
                "Position: {: >15} | Parent Position: {: >15} |".format(
                    position, parent
                ),
                node,
            )
            child_position = 0
            for child in node.children:
                queue.append((child, "{}{}".format(position, child_position), position))
                child_position += 1

    def __str__(self) -> str:
        if self.meta:
            return 'Node: "{}", "{}"'.format(self.type, self.meta)
        return 'Node: "{}"'.format(self.type)

    __repr__ = __str__


class ProgramNodeMeta:
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return "name: {}".format(self.name)


class FunctionNodeMeta:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __str__(self) -> str:
        return "name: {}, args: {}".format(self.name, self.args)


def reduced_print(p):
    matched_grammar = [(i.type, i.value) for i in p.slice[1:]]
    print(
        "\nReduced: {}: {}".format(
            p.slice[0], " ".join([i[0] for i in matched_grammar])
        )
    )
    for i in matched_grammar:
        print("**** {} {}".format(i[0], i[1]))


def p_program(p):
    """
    program : K_PROGRAM IDENTIFIER LCURLY program_body RCURLY
    """
    reduced_print(p)
    meta = ProgramNodeMeta(p[2])
    p[0] = Node(PROGRAM, meta=meta, children=[p[4]])


def p_program_body(p):
    """
    program_body : function program_body
                 | empty
    """
    reduced_print(p)
    if p[1].type == EMPTY:
        p[0] = Node(PROGRAM_BODY, children=[p[1]])
    else:
        p[0] = Node(
            PROGRAM_BODY,
            children=[p[1], *[child for child in p[2].children if child.type != EMPTY]],
        )


def p_function(p):
    """
    function : K_FUNCTION K_INTEGER IDENTIFIER LPAREN RPAREN LCURLY function_body RCURLY
    """
    reduced_print(p)
    meta = FunctionNodeMeta(name=p[3])
    p[0] = Node(FUNCTION, meta=meta, children=p[7])


def p_function_body(p):
    """
    function_body : statement function_body
                  | empty
    """
    reduced_print(p)
    if p[1].type == EMPTY:
        p[0] = Node(FUNCTION_BODY, children=[p[1]])
    else:
        p[0] = Node(
            FUNCTION_BODY,
            children=[p[1], *[child for child in p[2].children if child.type != EMPTY]],
        )


def p_statement(p):
    """
    statement : variable_definition SEMI
              | variable_declaration SEMI
              | variable_assignment SEMI
              | function_call SEMI

    """
    reduced_print(p)
    p[0] = Node(STATEMENT, children=p[1])


def p_function_call(p):
    """
    function_call : built_in_functions LPAREN function_call_args RPAREN
    """
    reduced_print(p)
    p[0] = Node(FUNCTION_CALL, children=[p[1], p[3]])


def p_built_in_functions(p):
    """
    built_in_functions : K_PRINT_INTEGER
                       | K_PRINT_STRING
    """
    reduced_print(p)
    p[0] = Node(p[1])


def p_function_call_args(p):
    """
    function_call_args : IDENTIFIER
                       | SCONSTANT
                       | empty
    """
    reduced_print(p)
    p[0] = Node(FUNCTION_CALL_ARGS, children=Node(p[1]))


def p_variable_assignment(p):
    """
    variable_assignment : IDENTIFIER ASSIGN expression
    """
    reduced_print(p)

    p[0] = Node(VARIABLE_ASSIGNMENT, children=[Node(p[1]), Node(ASSIGN), p[3]])


def p_variable_declaration(p):
    """
    variable_declaration : K_INTEGER IDENTIFIER ASSIGN expression
    """
    reduced_print(p)
    p[0] = Node(VARIABLE_DECLARATION, children=[Node(p[1]), Node(p[2]), p[4]])


def p_variable_definition(p):
    """
    variable_definition : K_INTEGER IDENTIFIER
    """
    reduced_print(p)
    p[0] = Node(VARIABLE_DEFINITION, children=[Node(p[2])])


def p_expression(p):
    """
    expression : term PLUS expression
               | MINUS expression
               | term MINUS expression
               | term
    """
    reduced_print(p)
    p[0] = Node(EXPRESSION, children=p[1])


def p_term(p):
    """
    term : factor DIVIDE term
         | factor MULTIPLY term
         | factor
    """
    reduced_print(p)
    p[0] = Node(TERM, children=Node(p[1]))


def p_factor(p):
    """
    factor : ICONSTANT
           | DCONSTANT
    """
    reduced_print(p)
    p[0] = Node(FACTOR, children=Node(p[1]))


def p_empty(p):
    """
    empty :
    """
    reduced_print(p)
    p[0] = Node(EMPTY)


# Build the parser
parser = yacc.yacc()

data = open(sys.argv[1], "r").read()
node = parser.parse(data)
Node.print_tree(node)
