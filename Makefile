BLUE=\033[0;34m
NC=\033[0m # No Color

# clean unwanted files and directories
clean-all: clean-deps clean-build clean-pyc
	@echo 'Running clean to reset project'

clean-packages:
	@echo 'Remove installed packages'
	@pip freeze --exclude-editable | xargs pip uninstall -y

clean-pyc:
	@echo 'Remove python artifacts'
	@rm -rf  __pycache__ .mypy_cache .pytest_cache htmlcov

clean-build:
	@echo 'Remove python artifacts'
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

# clean-deps: clean-packages
clean-deps: 
	@rm -f requirements.txt dev-requirements.txt

# compile prod and dev dependencies
compile-all: clean-all compile-dev
	@echo "${BLUE}Running clean-deps, compile-prod, and compile-dev${NC}"

compile-dev: compile-prod
	@echo "${BLUE}Creating dev-requirements.txt with requirements.txt constraint${NC}"
	@pip-compile dev-requirements.in

compile-prod:
	@echo "${BLUE}Creating requirements.txt from setup.py${NC}"
	@pip-compile

# install prod and dev dependencies
install-dev: compile-all
	@echo "${BLUE}Installing development dependencies${NC}"
	@pip-sync requirements.txt dev-requirements.txt

install-prod:
	@echo "${BLUE}Installing production dependencies${NC}"
	@pip-sync
	#
# code quality
format:
	@echo "${BLUE}Formatting files${NC}"
	@echo "${BLUE}Formatting with black${NC}"
	@black -S *.py
	@echo "${BLUE}Formatting with isort${NC}"
	@isort **/*.py

quality:
	@echo "${BLUE}Checking style on all files with flake8, pylint, mypy, bandit, detect-secrets, dependency-check, and safety${NC}"
	@echo "${BLUE}Running security check against source and test files${NC}"
	@bandit -lll --recursive .
	@echo "${BLUE}Running dependency check${NC}"
	# @dependency-check --scan . --out build --project "$(python ./setup.py --name)" --exclude ".git/**" --exclude "**/__pycache__/**" --exclude "htmlcov/**"
	@echo "${BLUE}Running secret detection${NC}"
	@detect-secrets scan
	@echo "${BLUE}Running safety dependency checker${NC}"
	@safety check -r requirements.txt -r dev-requirements.txt
	@echo "${BLUE}Running flake8 against source and test files${NC}"
	@flake8 src/ tests/
	@echo "${BLUE}Running pylint against source and test files${NC}"
	@pylint src/ tests/
	@echo "${BLUE}Running mypy against source and test files${NC}"
	@mypy --config-file setup.cfg src/ tests/
	@echo "${BLUE}Running yamllint against source and test files${NC}"
	@yamllint .

quality-diff:
	@echo "${BLUE}Checking style on all files with flake8, pylint, mypy, bandit, detect-secrets, dependency-check, and safety${NC}"
	@echo "${BLUE}Running security check against source and test files${NC}"
	@-bandit -lll --recursive .
	@echo "${BLUE}Running dependency check${NC}"
	# @-dependency-check --scan . --out build --project "$(python ./setup.py --name)" --exclude ".git/**" --exclude "**/__pycache__/**" --exclude "htmlcov/**"
	@echo "${BLUE}Running secret detection${NC}"
	@-detect-secrets scan
	@echo "${BLUE}Running safety dependency checker${NC}"
	@-safety check -r requirements.txt -r dev-requirements.txt
	@echo "${BLUE}Running flake8 against source and test files${NC}"
	@-flake8 src/ tests/
	@echo "${BLUE}Running pylint against source and test files${NC}"
	@-pylint src/ tests/
	@echo "${BLUE}Running mypy against source and test files${NC}"
	@-mypy --config-file setup.cfg src/ tests/
	@echo "${BLUE}Running yamllint against source and test files${NC}"
	@-yamllint .

test: clean-pyc
	@echo "${BLUE}Running .py tests${NC}"
	pytest
	@echo "${BLUE}Printing coverage${NC}"
	@coverage report -m
	@coverage xml -i

coverage:
	@echo "${BLUE}Generating coverage badge${NC}"
	@rm -f badges/coverage.svg
	@coverage-badge -o badges/coverage.svg

cov-html:
	@echo "${BLUE}Opening coverage html${NC}"
	@open htmlcov/index.html

help:
	@echo "		clean-deps		: Remove dependency files"
	@echo "		compile-all		: Run clean-deps, compile-prod, and compile-dev"
	@echo "		compile-dev		: Create dev-requirements.txt with requirements.txt constraint"
	@echo "		compile-prod	: Create requirements.txt from setup.py"
	@echo "		install-dev		: Install development dependencies"
	@echo "		install-prod	: Install production dependencies"
	@echo "		format			: Format files with black and isort"
	@echo "		quality			: Check style on all files with flake8, pylint, mypy, bandit, detect-secrets, and safety"
	@echo "		quality-diff	: Check diff style on all files with flake8, pylint, mypy, bandit, detect-secrets, and safety"
	@echo "		test			: Run .py tests"
	@echo "		coverage		: Generate coverage badge from code test coverage"
	@echo "		cov-html		: Open coverage report in browser"
