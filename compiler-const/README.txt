Course: COSC 5785-01
Group: Almountassir, Amit, Faith
Assignment: Symbol Table
----------------------------------


Requirements:


Our project uses Python. Running it requires you have a working Python environment installed, as well as the ply library (gotten from https://github.com/dabeaz/ply).


----------------------------------


Using the parser:


To run the parser, run "make" from the directory. The Makefile's first rule should automatically install ply and run simple_ast.py on te1.f23 for you.


To specify a file other than te1.f23, use the "make target FILE=<filename>" command.


If this results in any errors, possibly from your Python environment not being detectable or your system using the 'python3' command instead of 'python', then the parser can instead be run with the command "python simple_ast.py <filename>" or "python3 simple_ast.py <filename>".


While running, the compiler may automatically generate parser.out and parsetab.py. These are default files created by ply.


When starting up, the parser will print warnings for any terminals defined in the lexer but not used in the parser. These exist because this simple iteration of the parser handles a subset of the f23 language, enough to run te1.f23, te2.f23, and te3.f23, as instructed. When running, the parser will print the rules and tokens it's identifying as it parses the input. When finished, a banner is printed and the final walk through all the parse tree's nodes is given, with node IDs, contents, and which symbol table corresponds to the contents. After this, the contents of the symbol tables are also printed, with the key followed by its recorded properties.


Our parse tree (implemented as an abstract syntax tree) is traversed in breadth-first order. To illustrate what our generated parse tree looks like, the PNGs "example-parse-tree" 1-3 are included. The first two images show an example input and output, with the third being the illustrated tree of the output. Nodes are numbered according to their depth (with each deeper level being incremented by a power of 10) and how many nodes are on the level (with the hundreds place being incremented for each additional one).


If the input file is not a valid program in the f23 language (or is given terminals from it that it was not yet required to handle), it will print "syntax error" and exit.


The symbol table is implemented as linked hash tables, where one will exist for each scope. Entries in the table correspond to variables (names), where the values (constants) they hold are one of their stored properties. Constants not corresponding to variables, of a scope, are stored in a list. This list corresponds to the hash table entry called "CONSTANTS". Entries are added to the symbol table through an additional tree walk. The symbol table will also raise an exception if an undefined variable is used and give the line number it occurs on. See the PNGs "st-checking" 1-2 for an example of this, where the "c" variable is undefined and is caught by the symbol table.


----------------------------------


Submission details:


This submission includes a zip file with:
-this README
-rules.json (simple documentation of what our grammar rules are)
-simple_ast.py (parser)
-node_types.py (declares constants for use by the parser)
-symbol_table_properties.py (declares constants for use by the symbol table)
-Makefile
-te1.f23
-te2.f23
-te3.f23
-tedev.f23 (our group's test file for different .f23 files)
-example-parse-tree-[1-3].png
-st-checking-[1-2].png
-rules.json (simple documentation of what our grammar rules are)
-symbol_table.py (class for a symbol table)
-code_generation.py (the file which contains the functions that generate code for te2.f23)
-yourmain.h (target of code generation)
-f23.c (the virtual machine)


Each of us has also turned in an individual report.