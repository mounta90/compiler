# This file holds the functions that generate code WHILE PARSING.

import os

from node_types import *

# ------------------------------------------------
# A dictionary of the translations from .f23 to .c
# ------------------------------------------------
translations = {
    "main": "yourmain",
    "integer": "int",
}


# ----------------------------------------------------------------------------
# Takes a line of .f23 code, as input;
# Goes through the code and translates any .f23 keywords to the .c keywords.
# The translations use the 'translations' dictionary.
# ----------------------------------------------------------------------------
def translate(input_code: str) -> str:
    for old_code in translations.keys():
        input_code = input_code.replace(old_code, translations[old_code])

    return input_code


def generate_code_function(node):
    function_name = translate(node.meta.name)
    function_return_type = translate(node.meta.return_type)

    generated_code = "{} {}(){{\n\treturn 0;\n}}".format(
        function_return_type,
        function_name,
    )

    write_code(code_string=generated_code)


def generate_code_function_call(call_type: str, argument: str, mem_location: str):
    copy_string_line = "strcpy(&SMem[{}], {});\n\t".format(mem_location, argument)

    print_constant_line = "{}(&SMem[{}]);\n\t".format(call_type, mem_location)

    # Access Time:
    #   20 for SMem allocation of constant.
    #   100 for print_string function call.
    access_time = 20 + 100
    access_time_line = "F23_Time += {};\n\t".format(str(access_time))

    generated_code = copy_string_line + print_constant_line + access_time_line

    write_code(code_string=generated_code)


def write_code(code_string: str):
    # ----------------------------------------------------------------------------------------
    # Check if the C file is empty or not:
    #   If empty, use the "w" flag to write.
    #   If NOT empty, use the "a" flag to append to the file and not replace existing content.
    # ----------------------------------------------------------------------------------------
    if os.path.getsize("yourmain.h") == 0:
        with open("yourmain.h", "w") as file:
            file.write(code_string)

    else:
        with open("yourmain.h", "r") as read_file:
            file_code = read_file.read()

            file_code_parts = list(file_code.partition("return 0;"))

            index_of_return0 = file_code_parts.index("return 0;")

            file_code_parts.insert(index_of_return0, code_string)

            with open("yourmain.h", "w") as write_file:
                write_file.writelines(file_code_parts)
