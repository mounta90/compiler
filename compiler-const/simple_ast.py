import sys

import ply.yacc as yacc

from code_generation import *
from node_types import *
from symbol_table_properties import *
from simple_lex import tokens
from symbol_table import SymbolTable


symbol_table_hash_map = {}


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
        print("~ WALKING THROUGH THE AST ~")
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
            if isinstance(node, Node):
                for child in node.children:
                    queue.append(
                        (child, "{}{}".format(position, child_position), position)
                    )
                    child_position += 1

    @staticmethod
    def generate_symbol_tables(node):
        print()
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~ WALKING THROUGH THE AST ~")
        print("~ GENERATING SYMBOL TABLE ~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print()

        # ----------------------------------------------------
        # Generate symbol table for ROOT program node...
        # ----------------------------------------------------
        # This is the root program scope, so create a new symbol table; add to the symbol table hash map.
        program_symbol_table = SymbolTable(
            parent_table=None,
            scope=node.type,
            scope_name=node.meta.name,
        )

        program_st_key = str(program_symbol_table.scope_name)
        symbol_table_hash_map[program_st_key] = program_symbol_table

        level = "1"
        print(
            "Position: {: >10} | Symbol Table: {: >15} | Parent Symbol Table: {: >15} |".format(
                level,
                program_symbol_table.scope_name,
                "N/A",
            ),
            node,
        )
        queue = [
            (
                child,
                "{}{}".format(level, position),
                program_symbol_table,
                program_symbol_table,
            )
            for position, child in enumerate(node.children)
        ]

        while queue:
            node, position, node_st, parent_st = queue.pop(0)

            # ----------------------------------------------------
            # Generate symbol table for other nodes.
            # ----------------------------------------------------
            # In the case of a "function" or a "procedure" node:
            #   Generate a symbol table for it;
            #   Get its parent symbol table;
            #   Add it as the "function"/"procedure" parent symbol table;
            #   Add the "function"/"procedure" symbol table to the symbol tables hash map.
            # In the case of other nodes:
            #   Get its symbol table (node_st), which is passed down;
            #   Add to or manipulate the symbol table depending on what the node requires.
            # ----------------------------------------------------
            if node.type is FUNCTION:
                function_symbol_table = SymbolTable(
                    scope=node.type,
                    scope_name=node.meta.name,
                    parent_table=parent_st,
                )

                function_st_key = str(function_symbol_table.scope_name)
                symbol_table_hash_map[function_st_key] = function_symbol_table

                child_position = 0
                if isinstance(node, Node):
                    for child in node.children:
                        queue.append(
                            (
                                child,
                                "{}{}".format(position, child_position),
                                function_symbol_table,
                                parent_st,
                            ),
                        )
                        child_position += 1

                print(
                    "Position: {: >10} | Symbol Table: {: >15} | Parent Symbol Table: {: >15} |".format(
                        position,
                        function_symbol_table.scope_name,
                        parent_st.scope_name,
                    ),
                    node,
                )

            elif node.type is PROCEDURE:
                procedure_symbol_table = SymbolTable(
                    scope=node.type,
                    scope_name=node.meta.name,
                    parent_table=parent_st,
                )

                # If the procedure has parameters, add them to the symbol table
                try:
                    procedure_parameter_dtype = node.meta.args[0][0]
                    procedure_parameter_identifier = node.meta.args[0][1]

                    procedure_symbol_table.put(
                        symbol=procedure_parameter_identifier,
                        property_key=DATA_TYPE,
                        property_value=procedure_parameter_dtype,
                    )
                except:
                    # Nothing, the procedure has no parameters to add to symbol table
                    pass

                procedure_st_key = str(procedure_symbol_table.scope_name)
                symbol_table_hash_map[procedure_st_key] = procedure_symbol_table

                child_position = 0
                if isinstance(node, Node):
                    for child in node.children:
                        queue.append(
                            (
                                child,
                                "{}{}".format(position, child_position),
                                procedure_symbol_table,
                                parent_st,
                            ),
                        )
                        child_position += 1

                print(
                    "Position: {: >10} | Symbol Table: {: >15} | Parent Symbol Table: {: >15} |".format(
                        position,
                        procedure_symbol_table.scope_name,
                        parent_st.scope_name,
                    ),
                    node,
                )

            else:
                symbol_table = node_st

                if node.type is VARIABLE_DEFINITION:
                    # "variable_definition" will only have 2 types of children:
                    #   * DTYPE
                    #   * IDENTIFIER
                    symbol = None
                    dtype = None
                    for child in node.children:
                        if child.type is IDENTIFIER:
                            # Create a new symbol table entry for this IDENTIFIER:
                            symbol = child.meta.name
                        else:
                            # symbol = SymbolProperties(data_type=child.meta.dtype)
                            dtype = child.meta.dtype

                    # Place in the symbol table, for symbol, the property.
                    # This property can then be accessed with: symbol_table[symbol][property].
                    symbol_table.put(
                        symbol=symbol, property_key=DATA_TYPE, property_value=dtype
                    )

                elif node.type is VARIABLE_ASSIGNMENT:
                    # "variable_assignment" will only have 3 types of children:
                    #   * IDENTIFIER
                    #   * ASSIGN
                    #   * expression
                    id_name = None
                    id_value = None
                    for child in node.children:
                        if child.type is IDENTIFIER:
                            id_name = child.meta.name
                        elif child.type is EXPRESSION:
                            # Get the value of this expression node;
                            # The value is returned as a list:
                            id_value: list = get_expression_value(
                                child,
                                expression_list=[],
                            )
                        else:
                            # This is where the ASSIGN node goes to;
                            # Nothing is done here.
                            pass

                    # Add to symbol table;
                    # BEFORE adding to symbol table,
                    # Check the current symbol table and parent tables for the value of this IDENTIFIER.
                    # If it exists, update its value;
                    # Otherwise, throw an error.
                    current_symbol_table = symbol_table
                    while current_symbol_table is not None:
                        if current_symbol_table.is_present(id_name):
                            # Update the symbol value in the symbol table.
                            # current_symbol_table.put(key=id_name, value=id_value)
                            current_symbol_table.put(
                                symbol=id_name,
                                property_key=VALUE,
                                property_value=id_value,
                            )
                            break
                        current_symbol_table = current_symbol_table.parent_table
                    else:
                        print(
                            'Error! Identifier "%s" not defined, found at line number PLACE_LINE_NUMBER_HERE.'
                            % id_name
                        )
                        exit(0)

                elif node.type is PROCEDURE_CALL:
                    # For this node, we want to update the parameter value of the procedure symbol table.
                    procedure_identifier = node.meta.name
                    procedure_argument_node = node.children[0].children[0]
                    procedure_argument_identifier = procedure_argument_node.meta.name
                    procedure_argument_value = symbol_table.table[
                        procedure_argument_identifier
                    ][VALUE]

                    symbol_table_hash_map[procedure_identifier].table[
                        procedure_argument_identifier
                    ][VALUE] = procedure_argument_value

                elif node.type is CONSTANT:
                    # For this node, we want to add its constant to its scope symbol table.
                    constant_dtype = node.meta.dtype
                    constant_value = node.meta.value
                    symbol_table.put_constant(
                        const_dtype=constant_dtype,
                        const_value=constant_value,
                    )

                child_position = 0
                if isinstance(node, Node):
                    for child in node.children:
                        queue.append(
                            (
                                child,
                                "{}{}".format(position, child_position),
                                node_st,
                                parent_st,
                            ),
                        )
                        child_position += 1

                print(
                    "Position: {: >10} | Symbol Table: {: >15} | ".format(
                        position,
                        node_st.scope_name,
                    ),
                    node,
                )

    @staticmethod
    def walk_tree_generate_code(node):
        print()
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("~ WALKING THROUGH THE AST ~")
        print("~ GENERATING CODE ~")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print()

        program_symbol_table = symbol_table_hash_map[node.meta.name]
        level = "1"
        print(
            "Position: {: >10} | Symbol Table: {: >15} | Parent Symbol Table: {: >15} |".format(
                level,
                program_symbol_table.scope_name,
                "N/A",
            ),
            node,
        )
        queue = [
            (
                child,
                "{}{}".format(level, position),
                program_symbol_table,
                program_symbol_table,
            )
            for position, child in enumerate(node.children)
        ]

        while queue:
            node, position, node_st, parent_st = queue.pop(0)

            if node.type is FUNCTION:
                # Get the function symbol table;
                # Pass it down to its children:
                function_symbol_table = symbol_table_hash_map[node.meta.name]

                # Generate code for this 'function' node:
                generate_code_function(node)

                child_position = 0
                if isinstance(node, Node):
                    for child in node.children:
                        queue.append(
                            (
                                child,
                                "{}{}".format(position, child_position),
                                function_symbol_table,
                                parent_st,
                            ),
                        )
                        child_position += 1

                print(
                    "Position: {: >10} | Symbol Table: {: >15} | Parent Symbol Table: {: >15} |".format(
                        position,
                        function_symbol_table.scope_name,
                        parent_st.scope_name,
                    ),
                    node,
                )

            # TODO: Place an elif for PROCEDURE here:

            else:
                current_symbol_table = node_st

                if node.type == FUNCTION_CALL:
                    # Walk its left branch to get the function call type.
                    # The function call type will directly be the first child in the left branch.
                    function_call_type_node = node.children[0]
                    function_call_type = function_call_type_node.type

                    # Walk its right branch to get the function call argument value.
                    right_node = node.children[1]
                    function_call_argument_value_node = get_function_call_argument(
                        right_node
                    )

                    # -------------------------
                    # There are 2 types of args:
                    #   CONSTANT -> Get value from node.
                    #   IDENTIFIER -> Get value corresponding to IDENTIFIER from symbol table.
                    # -------------------------
                    if function_call_argument_value_node.type == IDENTIFIER:
                        identifier_name = function_call_argument_value_node.meta.name
                        # TODO: Left off here...
                        print("PRINTING SYMBOL TABLE...")
                        print(current_symbol_table)
                    else:
                        function_call_argument_value = (
                            function_call_argument_value_node.meta.value
                        )
                        function_call_argument_dtype = (
                            function_call_argument_value_node.meta.dtype
                        )

                    # Retrieve the constant/variable in the symbol table.
                    # Allocate space in memory for the constant/variable.
                    function_call_argument_mem_location = None
                    const_list = current_symbol_table.table["CONSTANTS"]
                    for const in const_list:
                        if (
                            const[DTYPE] == function_call_argument_dtype
                            and const[VALUE] == function_call_argument_value
                        ):
                            if function_call_argument_dtype == "SCONSTANT":
                                # Memory value is the argument length + 1 for the end of string in C.
                                # Subtract 2 from length to account for the quotation marks.
                                mem_value = len(function_call_argument_value) - 2 + 1
                                const[MEM_LOCATION] = mem_value

                                # Get the memory location of the function call argument:
                                function_call_argument_mem_location = str(mem_value)

                    # Pass this information to the code generation function.
                    #   - function call type
                    #   - constant value
                    #   - constant memory location
                    generate_code_function_call(
                        call_type=function_call_type,
                        argument=function_call_argument_value,
                        mem_location=function_call_argument_mem_location,
                    )

                child_position = 0
                if isinstance(node, Node):
                    for child in node.children:
                        queue.append(
                            (
                                child,
                                "{}{}".format(position, child_position),
                                node_st,
                                parent_st,
                            ),
                        )
                        child_position += 1

                print(
                    "Position: {: >10} | Symbol Table: {: >15} | ".format(
                        position,
                        node_st.scope_name,
                    ),
                    node,
                )

    def __repr__(self) -> str:
        if self.meta:
            return "<Node: {}, Meta: {}>".format(self.type, self.meta)
        return "<Node: {}>".format(self.type)


def get_function_call_argument(node: Node):
    while node:
        if node.type == IDENTIFIER or node.type == CONSTANT:
            print("PRINTING FROM INSIDE IF...")
            print(node.type)
            return node
        else:
            print("PRINTING FROM INSIDE ELSE...")
            print(node.type)
            node = node.children[0]


def get_expression_value(node: Node, expression_list: list):
    # Expression has 3 child nodes (presently):
    #   left: termNode
    #   center: operatorNode
    #   right: expressionNode
    # Recursively traverse the node in In-Order Binary traversal;
    # BASE CASE - the node is a CONSTANT or an IDENTIFIER.

    if node is not None:
        # ----------------------
        # BASE CASE: CONSTANT or IDENTIFIER
        # ----------------------
        if node.type is CONSTANT or node.type is IDENTIFIER:
            expression_list.append(node)
        # ----------------------

        node_children_amount = len(node.children)
        for i in range(0, node_children_amount):
            if i == 0:
                left_node = node.children[i]
                get_expression_value(left_node, expression_list)
            elif i == 1:
                center_node = node.children[i]
                expression_list.append(center_node)
            else:
                right_node = node.children[i]
                get_expression_value(right_node, expression_list)
    return expression_list


def is_node(obj):
    return isinstance(obj, Node)


class ProgramNodeMeta:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ProgramNodeMeta: NAME({})>".format(self.name)


class FunctionNodeMeta:
    def __init__(self, name, return_type, *args):
        self.name = name
        self.return_type = return_type
        self.args = args

    def __repr__(self):
        return "<FunctionNodeMeta: NAME({}) RETURN-TYPE({})>".format(
            self.name, self.return_type
        )


class ProcedureNodeMeta:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return "<ProcedureNodeMeta: NAME({}) ARG-TYPES{}>".format(self.name, self.args)


class ProcedureCallNodeMeta:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ProcedureCallNodeMeta: NAME({})>".format(self.name)


class ConstantNodeMeta:
    def __init__(self, value, dtype) -> None:
        self.value = value
        self.dtype = dtype

    def __repr__(self) -> str:
        return "<ConstantNodeMeta: DTYPE({}) VALUE({})>".format(
            self.dtype,
            self.value,
        )


class IdentifierNodeMeta:
    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return "<IdentifierNodeMeta: NAME({})>".format(self.name)


class OperatorNodeMeta:
    def __init__(self, operator):
        self.operator = operator

    def __repr__(self):
        return "<OperatorNodeMeta: VALUE({})>".format(self.operator)


class ComparisonNodeMeta:
    def __init__(self, comparison):
        self.comparison = comparison

    def __repr__(self):
        return "<ComparisonNodeMeta: VALUE({})>".format(self.comparison)


class DataTypeNodeMeta:
    def __init__(self, dtype):
        self.dtype = dtype

    def __repr__(self):
        return "<DataTypeNodeMeta: VALUE({})>".format(self.dtype)


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
    p[0] = Node(PROGRAM, meta=meta, children=[c for c in p[4]])


def p_program_body(p):
    """
    program_body : function program_body
                 | procedure program_body
                 | empty
    """
    reduced_print(p)
    if p[1].type == EMPTY:
        p[0] = p[1]
    else:
        siblings = []
        if isinstance(p[2], list):
            siblings = [s for s in p[2] if s.type != EMPTY]
        p[0] = [p[1], *siblings] if siblings else [p[1]]


def p_function(p):
    """
    function : K_FUNCTION K_INTEGER IDENTIFIER LPAREN arguments RPAREN LCURLY scope_body RCURLY
             | K_FUNCTION K_DOUBLE IDENTIFIER LPAREN arguments RPAREN LCURLY scope_body RCURLY
             | K_FUNCTION K_STRING IDENTIFIER LPAREN arguments RPAREN LCURLY scope_body RCURLY
    """
    reduced_print(p)

    meta = FunctionNodeMeta(name=p[3], return_type=p[2])
    p[0] = Node(FUNCTION, meta=meta, children=[p[5], p[8]])


def p_procedure(p):
    """
    procedure : K_PROCEDURE IDENTIFIER LPAREN RPAREN LCURLY scope_body RCURLY
    """
    reduced_print(p)

    procedure_meta = ProcedureNodeMeta(name=p[2])
    p[0] = Node(PROCEDURE, meta=procedure_meta, children=p[6])


def p_procedure_with_args(p):
    """
    procedure : K_PROCEDURE IDENTIFIER LPAREN arguments RPAREN LCURLY scope_body RCURLY
    """
    reduced_print(p)

    procedure_meta = ProcedureNodeMeta(p[2], p[4])

    p[0] = Node(PROCEDURE, meta=procedure_meta, children=[p[4], p[7]])


def p_arguments(p):
    """
    arguments : variable_definition arguments
    """
    reduced_print(p)
    p[0] = Node(ARGUMENTS, children=[p[1], p[2]])


def p_arguments_with_comma(p):
    """
    arguments : COMMA arguments
    """
    reduced_print(p)
    p[0] = Node(ARGUMENTS, children=[p[2]])


def p_arguments_empty(p):
    """
    arguments : empty
    """
    p[0] = p[1]


def p_scope_body(p):
    """
    scope_body : statement scope_body
               | function scope_body
               | procedure scope_body
               | empty
    """
    reduced_print(p)
    if p[1].type == EMPTY:
        p[0] = p[1]
    else:
        siblings = []
        # TODO : check this for proper output.
        if isinstance(p[2], list):
            siblings = [s for s in p[2] if s.type != EMPTY]
        p[0] = (
            Node(SCOPE_BODY, children=[p[1], *siblings])
            if siblings
            else Node(SCOPE_BODY, children=[p[1]])
        )


def p_statement(p):
    """
    statement : variable_definition SEMI
              | variable_declaration SEMI
              | variable_assignment SEMI
              | function_call SEMI
              | function_return SEMI
              | procedure_call SEMI
              | variable_decrement_increment SEMI
    """
    reduced_print(p)
    p[0] = Node(STATEMENT, children=p[1])


def p_statement_looping(p):
    """
    statement : if_statement
              | do_statement
              | while_statement
    """
    reduced_print(p)
    p[0] = Node(STATEMENT, children=p[1])


def p_while_statement_with_braces(p):
    """
    while_statement : K_WHILE LPAREN boolean_logic RPAREN LCURLY scope_body RCURLY
    """
    reduced_print(p)
    p[0] = Node(WHILE, children=[p[3], p[6]])


def p_while_statement_without_braces(p):
    """
    while_statement : K_WHILE LPAREN boolean_logic RPAREN statement
    """
    reduced_print(p)
    p[0] = Node(WHILE, children=[p[3], p[5]])


def p_do_statement(p):
    """
    do_statement : K_DO LPAREN variable_assignment SEMI boolean_logic SEMI variable_assignment RPAREN LCURLY scope_body RCURLY
                 | K_DO LPAREN variable_definition SEMI boolean_logic SEMI variable_assignment RPAREN LCURLY scope_body RCURLY
                 | K_DO LPAREN variable_assignment SEMI boolean_logic SEMI variable_decrement_increment RPAREN LCURLY scope_body RCURLY
                 | K_DO LPAREN variable_definition SEMI boolean_logic SEMI variable_decrement_increment RPAREN LCURLY scope_body RCURLY
    """
    reduced_print(p)
    p[0] = Node(DO, children=[p[3], p[5], p[7], p[10]])


def p_do_statement_without_braces(p):
    """
    do_statement : K_DO LPAREN variable_assignment SEMI boolean_logic SEMI variable_assignment RPAREN statement
                 | K_DO LPAREN variable_definition SEMI boolean_logic SEMI variable_assignment RPAREN statement
                 | K_DO LPAREN variable_assignment SEMI boolean_logic SEMI variable_decrement_increment RPAREN statement
                 | K_DO LPAREN variable_definition SEMI boolean_logic SEMI variable_decrement_increment RPAREN statement
    """
    reduced_print(p)
    p[0] = Node(DO, children=[p[3], p[5], p[7], p[9]])


def p_if_statement_only(p):
    """
    if_statement : if
    """
    reduced_print(p)
    p[0] = Node(IF, children=p[1])


def p_if_statement(p):
    """
    if_statement : if K_ELSE after_else
    """
    reduced_print(p)
    p[0] = Node(IF, children=[p[1], p[3]])


def p_if_without_braces(p):
    """
    if : K_IF LPAREN boolean_logic RPAREN K_THEN statement
    """
    reduced_print(p)
    p[0] = Node(IF, children=[p[3], p[6]])


def p_if_with_braces(p):
    """
    if : K_IF LPAREN boolean_logic RPAREN K_THEN LCURLY scope_body RCURLY
    """
    reduced_print(p)
    p[0] = Node(IF, children=[p[3], p[7]])


def p_if_empty(p):
    """
    if : empty
    """
    reduced_print(p)
    p[0] = p[1]


def p_after_else_1_without_braces(p):
    """
    after_else : statement
    """
    # This "after else" parses the case where only an 'else' comes after.
    reduced_print(p)
    p[0] = Node(AFTER_ELSE_ELSE, children=[p[1]])


def p_after_else_1_with_braces(p):
    """
    after_else : LCURLY scope_body RCURLY
    """
    # This "after else" parses the case where only an 'else' comes after.
    reduced_print(p)
    p[0] = Node(AFTER_ELSE_ELSE, children=[p[2]])


def p_after_else_2(p):
    """
    after_else : if K_ELSE after_else
    """
    # This "after else" parses the case where one or more 'else if' come after.
    reduced_print(p)
    p[0] = Node(AFTER_ELSE_ELSE_IF, children=[p[1], p[3]])


def p_built_in_function_call(p):
    """
    function_call : built_in_functions LPAREN function_call_args RPAREN
    """
    reduced_print(p)
    p[0] = Node(FUNCTION_CALL, children=[p[1], p[3]])


def p_created_function_call(p):
    """
    function_call : IDENTIFIER LPAREN function_call_args RPAREN
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FUNCTION_CALL, children=[id_node, p[3]])


def p_function_return_identifier(p):
    """
    function_return : K_RETURN IDENTIFIER
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[2])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FUNCTION_RETURN, children=[id_node])


def p_function_return_constant(p):
    """
    function_return : K_RETURN ICONSTANT
                    | K_RETURN DCONSTANT
                    | K_RETURN SCONSTANT
    """
    reduced_print(p)

    constant_meta = ConstantNodeMeta(value=p[2], dtype=p.slice[2].type)
    constant_node = Node(CONSTANT, meta=constant_meta)

    p[0] = Node(FUNCTION_RETURN, children=[constant_node])


def p_function_return_other(p):
    """
    function_return : K_RETURN function_call
                    | K_RETURN variable_assignment
    """
    reduced_print(p)

    p[0] = Node(FUNCTION_RETURN, children=[p[2]])


def p_procedure_call(p):
    """
    procedure_call : IDENTIFIER LPAREN procedure_call_args RPAREN
    """
    reduced_print(p)
    procedure_call_meta = ProcedureCallNodeMeta(name=p[1])
    p[0] = Node(PROCEDURE_CALL, meta=procedure_call_meta, children=p[3])


def p_built_in_functions(p):
    """
    built_in_functions : K_PRINT_INTEGER
                       | K_PRINT_DOUBLE
                       | K_PRINT_STRING
                       | K_READ_INTEGER
                       | K_READ_DOUBLE
                       | K_READ_STRING
    """
    reduced_print(p)
    p[0] = Node(p[1])


def p_procedure_call_args(p):
    """
    procedure_call_args : identifiers
                        | term
    """
    reduced_print(p)

    p[0] = Node(PROCEDURE_CALL_ARGS, children=[p[1]])


def p_function_call_args(p):
    """
    function_call_args : identifiers function_call_args
                       | term function_call_args
                       | empty
    """
    reduced_print(p)
    if p[1].type == EMPTY:
        p[0] = p[1]
    else:
        p[0] = Node(FUNCTION_CALL_ARGS, children=[p[1], p[2]])


def p_variable_decrement_increment(p):
    """
    variable_decrement_increment : IDENTIFIER INCREMENT
                                 | IDENTIFIER DECREMENT
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)

    inc_dec_node = Node(p[2])

    p[0] = Node(VARIABLE_DECREMENT_INCREMENT, children=[id_node, inc_dec_node])


def p_variable_assignment(p):
    """
    variable_assignment : IDENTIFIER ASSIGN variable_assignment
                        | IDENTIFIER ASSIGN function_call
                        | IDENTIFIER ASSIGN expression
                        | IDENTIFIER ASSIGN_DIVIDE expression
                        | IDENTIFIER ASSIGN_MULTIPLY expression
                        | IDENTIFIER ASSIGN_PLUS expression
                        | IDENTIFIER ASSIGN_MINUS expression
                        | IDENTIFIER ASSIGN_MOD expression
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    p[0] = Node(
        VARIABLE_ASSIGNMENT,
        children=[Node(IDENTIFIER, meta=id_meta), Node(p[2]), p[3]],
    )


def p_variable_assignment_array(p):
    """
    variable_assignment : IDENTIFIER LBRACKET expression RBRACKET ASSIGN variable_assignment
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN function_call
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN expression
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN_DIVIDE expression
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN_MULTIPLY expression
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN_PLUS expression
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN_MINUS expression
                        | IDENTIFIER LBRACKET expression RBRACKET ASSIGN_MOD expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN variable_assignment
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN_DIVIDE expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN_MULTIPLY expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN_PLUS expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN_MINUS expression
                        | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET ASSIGN_MOD expression
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    # TODO : take care of array element location expression
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(VARIABLE_ASSIGNMENT, children=[id_node, p[3], p[5], p[6]])


def p_variable_declaration(p):
    """
    variable_declaration : variable_definition ASSIGN expression identifiers
    """
    reduced_print(p)

    p[0] = Node(
        VARIABLE_DECLARATION,
        children=[p[1], Node(ASSIGN), p[3], p[4]],
    )


def p_variable_definition(p):
    """
    variable_definition : K_INTEGER identifiers
                        | K_DOUBLE identifiers
                        | K_STRING identifiers
    """
    reduced_print(p)

    dtype_meta = DataTypeNodeMeta(dtype=p[1])
    dtype_node = Node(DTYPE, meta=dtype_meta)

    p[0] = Node(
        VARIABLE_DEFINITION,
        children=[dtype_node, p[2]],
    )


def p_identifiers(p):
    """
    identifiers : IDENTIFIER identifiers
    """
    reduced_print(p)
    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)
    p[0] = Node(IDENTIFIERS, children=[id_node, p[2]])


def p_identifiers_array(p):
    """
    identifiers : IDENTIFIER LBRACKET expression RBRACKET identifiers
                | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET identifiers
    """
    reduced_print(p)
    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)
    p[0] = Node(IDENTIFIERS, children=[id_node, p[3], p[5]])


def p_identifiers_comma(p):
    """
    identifiers : COMMA identifiers
    """
    reduced_print(p)
    p[0] = Node(IDENTIFIERS, children=p[2])


def p_identifiers_empty(p):
    """
    identifiers : empty
    """
    reduced_print(p)
    p[0] = p[1]


def p_variable_definition_array(p):
    """
    variable_definition : K_INTEGER IDENTIFIER LBRACKET RBRACKET
                        | K_DOUBLE IDENTIFIER LBRACKET RBRACKET
                        | K_STRING IDENTIFIER LBRACKET RBRACKET
    """
    reduced_print(p)
    dtype_meta = DataTypeNodeMeta(dtype=p[1])
    dtype_node = Node(DTYPE, meta=dtype_meta)

    id_meta = IdentifierNodeMeta(name=p[2])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(ARRAY_VARIABLE_DEFINITION, children=[dtype_node, id_node])


def p_variable_definition_array_other(p):
    """
    variable_definition : K_INTEGER IDENTIFIER LBRACKET expression RBRACKET
                        | K_DOUBLE IDENTIFIER LBRACKET expression RBRACKET
                        | K_STRING IDENTIFIER LBRACKET expression RBRACKET
                        | K_INTEGER IDENTIFIER LBRACKET variable_decrement_increment RBRACKET
                        | K_DOUBLE IDENTIFIER LBRACKET variable_decrement_increment RBRACKET
                        | K_STRING IDENTIFIER LBRACKET variable_decrement_increment RBRACKET
    """
    reduced_print(p)
    dtype_meta = DataTypeNodeMeta(dtype=p[1])
    dtype_node = Node(DTYPE, meta=dtype_meta)

    id_meta = IdentifierNodeMeta(name=p[2])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(ARRAY_VARIABLE_DEFINITION, children=[dtype_node, id_node, p[4]])


def p_boolean_logic_1(p):
    """
    boolean_logic : arithmetic_logic DAND arithmetic_logic
                  | arithmetic_logic DOR arithmetic_logic
    """
    reduced_print(p)
    comparison_meta = ComparisonNodeMeta(comparison=p[2])

    p[0] = Node(
        BOOLEAN_LOGIC,
        children=[
            p[1],
            Node(COMPARISON, meta=comparison_meta),
            p[3],
        ],
    )


def p_boolean_logic_2(p):
    """
    boolean_logic : NOT arithmetic_logic
    """
    reduced_print(p)

    comparison_meta = ComparisonNodeMeta(comparison=p[1])

    p[0] = Node(
        BOOLEAN_LOGIC,
        children=[
            Node(COMPARISON, meta=comparison_meta),
            p[2],
        ],
    )


def p_boolean_logic_3(p):
    """
    boolean_logic : arithmetic_logic
    """
    reduced_print(p)

    p[0] = Node(BOOLEAN_LOGIC, children=[p[1]])


def p_arithmetic_logic_function_call(p):
    """
    arithmetic_logic : function_call DEQ function_call
                     | function_call GEQ function_call
                     | function_call GT function_call
                     | function_call LEQ function_call
                     | function_call LT function_call
                     | function_call NE function_call
                     | function_call DEQ expression
                     | function_call GEQ expression
                     | function_call GT expression
                     | function_call LEQ expression
                     | function_call LT expression
                     | function_call NE expression
    """
    reduced_print(p)

    comparison_meta = ComparisonNodeMeta(comparison=p[2])

    p[0] = Node(
        ARITHMETIC_LOGIC,
        children=[
            p[1],
            Node(COMPARISON, meta=comparison_meta),
            p[3],
        ],
    )


def p_arithmetic_logic_expression(p):
    """
    arithmetic_logic : expression DEQ expression
                     | expression GEQ expression
                     | expression GT expression
                     | expression LEQ expression
                     | expression LT expression
                     | expression NE expression
                     | expression DEQ function_call
                     | expression GEQ function_call
                     | expression GT function_call
                     | expression LEQ function_call
                     | expression LT function_call
                     | expression NE function_call
    """
    reduced_print(p)

    comparison_meta = ComparisonNodeMeta(comparison=p[2])

    p[0] = Node(
        ARITHMETIC_LOGIC,
        children=[
            p[1],
            Node(COMPARISON, meta=comparison_meta),
            p[3],
        ],
    )


def p_expression_term_plus_minus_expression(p):
    """
    expression : term PLUS expression
               | term MINUS expression
    """
    reduced_print(p)
    operator_meta = OperatorNodeMeta(operator=p[2])
    p[0] = Node(
        EXPRESSION,
        children=[
            p[1],
            Node(OPERATOR, meta=operator_meta),
            p[3],
        ],
    )


def p_expression_term(p):
    """
    expression : term
    """
    reduced_print(p)
    p[0] = Node(EXPRESSION, children=p[1])


def p_term_factor_divide_multiply_term(p):
    """
    term : factor DIVIDE term
         | factor MULTIPLY term
         | factor MOD term
    """
    reduced_print(p)
    operator_meta = OperatorNodeMeta(operator=p[2])
    p[0] = Node(TERM, children=[p[1], Node(OPERATOR, meta=operator_meta), p[3]])


def p_term_factor(p):
    """
    term : factor
    """
    reduced_print(p)
    p[0] = Node(TERM, children=p[1])


def p_factor_paren_expression(p):
    """
    factor : LPAREN expression RPAREN
    """
    reduced_print(p)

    p[0] = Node(FACTOR, children=p[2])


def p_factor_constant(p):
    """
    factor : ICONSTANT
           | DCONSTANT
           | SCONSTANT
    """
    reduced_print(p)

    constant_meta = ConstantNodeMeta(value=p[1], dtype=p.slice[1].type)
    constant_node = Node(CONSTANT, meta=constant_meta)

    p[0] = Node(FACTOR, children=constant_node)


def p_factor_negative_constant(p):
    """
    factor : MINUS ICONSTANT
           | MINUS DCONSTANT
    """
    reduced_print(p)
    constant_meta = ConstantNodeMeta(value=p[2], dtype=p.slice[2].type)
    constant_node = Node(CONSTANT, meta=constant_meta)

    p[0] = Node(FACTOR, children=[p[1], constant_node])


def p_factor_identifier(p):
    """
    factor : IDENTIFIER
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FACTOR, children=id_node)


def p_factor_negative_identifier(p):
    """
    factor : MINUS IDENTIFIER
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[2])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FACTOR, children=[p[1], id_node])


def p_factor_array_identifier(p):
    """
    factor : IDENTIFIER LBRACKET expression RBRACKET
           | IDENTIFIER LBRACKET variable_decrement_increment RBRACKET
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[1])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FACTOR, children=[id_node, p[3]])


def p_factor_array_negative_identifier(p):
    """
    factor : MINUS IDENTIFIER LBRACKET expression RBRACKET
           | MINUS IDENTIFIER LBRACKET variable_decrement_increment RBRACKET
    """
    reduced_print(p)

    id_meta = IdentifierNodeMeta(name=p[2])
    id_node = Node(IDENTIFIER, meta=id_meta)

    p[0] = Node(FACTOR, children=[p[1], id_node, p[4]])


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
# Node.generate_symbol_tables(node)
# Node.walk_tree_generate_code(node)


# print()
# print()
# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print("~ DISPLAYING SYMBOL TABLES ~")
# print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print()
#
# for key in symbol_table_hash_map.keys():
#     print(symbol_table_hash_map[key])
#
# print()
