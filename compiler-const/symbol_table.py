# ---Symbol Table--- #
# A symbol table as a python dictionary, with its APIs.
# A python dictionary is by default a hash table, with O(1) insertion & O(1) look-up.
from symbol_table_properties import VALUE


class SymbolTable:
    parent_table = None
    scope = None
    scope_name = None

    def __init__(self, scope=None, scope_name=None, parent_table=None):
        self.table = {}

        if scope:
            self.scope = scope
        if scope_name:
            self.scope_name = scope_name
        if parent_table:
            self.parent_table = parent_table

    # size() => returns size of symbol table.
    def size(self):
        return len(self.table)

    # is_empty() => returns a boolean value of whether the symbol table is empty or not.
    def is_empty(self):
        return self.size() == 0

    # get_keys() => returns all keys of the symbol table, as a list.
    def get_keys(self):
        return list(self.table.keys())

    # is_present(key) => returns a boolean value based on whether a symbol is present, given a key as a parameter.
    def is_present(self, key):
        return key in self.table.keys()

    # get(key) => returns the symbol table value, associated with the key given as parameter, from the symbol table.
    def get(self, key):
        return self.table[key]

    # put(symbol, property_key, property_value) => adds a <key, value> pair for a symbol in the symbol table
    # OR replaces the value corresponding to the key.
    def put(self, symbol, property_key, property_value):
        if self.table.get(symbol) is not None:
            # TODO: Take care of trailing zeros.
            self.table[symbol][property_key] = property_value
        else:
            self.table[symbol] = {}
            self.table[symbol][property_key] = property_value

    def put_constant(self, const_dtype, const_value):
        # NOTE: duplicate constants need to be taken care of.

        const_object = {
            "data_type": const_dtype,
            "value": const_value,
        }

        if self.table.get("CONSTANTS") is not None:
            self.table["CONSTANTS"].append(const_object)
        else:
            self.table["CONSTANTS"] = []
            self.table["CONSTANTS"].append(const_object)

    # delete(key) => deletes a <key, value> pair, associated with the key given as a parameter,
    # from the symbol table; returns the deleted key if one needs to check what was deleted.
    def delete(self, key):
        if self.is_present(key):
            self.table.pop(key)

    def __repr__(self):
        return "Symbol Table\nSCOPE - {scope}\nSCOPE NAME - {scope_name}\nPARENT TABLE - {parent_table}\n\t {table}\n".format(
            scope=self.scope,
            scope_name=self.scope_name,
            parent_table=self.parent_table.scope_name
            if self.parent_table is not None
            else str(None),
            table=self.table,
        )
