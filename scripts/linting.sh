# Black
ECHO Running black...
black src/

# Flake
ECHO Running flake...
flake8 src/

# Isort
ECHO Running isort...
isort src/

#Pydocstyle
ECHO Running pydocstyle...
pydocstyle src/

# Mypy
ECHO Running mypy...
mypy src/
