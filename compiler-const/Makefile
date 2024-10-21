# Makefile
# 'make' with no arguments runs the first rule (run)


# run parser
run: build simple_lex.py simple_ast.py
	@echo "Running the parser on te2.f23"
	python simple_ast.py te2.f23


# install the dependencies
build: 
	@echo "Installing dependency 'ply'"
	pip install ply


# run parser on file specified in command line
target: build simple_lex.py simple_ast.py
	@echo "Running the parser on input"
	python simple_ast.py $(FILE)

# print options
help:
	@echo "Your options are the following:"
	@echo "    make run"
	@echo "        Installs dependencies and runs the parser on te2.f23"
	@echo "    make target FILE=<filename>"
	@echo "        Installs dependencies and runs the parser on the specified file"
	@echo "    make clean"
	@echo "        Removes extra files, but leaves lexer and parser files intact"
	@echo "    make help"
	@echo "        Prints a help message"

# clean up pycache folder
clean:
	rm -rf __pycache__
