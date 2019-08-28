Inside `docs` directory:

To update module list:

    export SPHINX_APIDOC_OPTIONS=members,show-inheritance
    sphinx-apidoc -f -o source/ ..

(Remove the `-f` flag on `sphinx-apidoc` to avoid overwriting existing files)

To make html docs:

    make html
    x-www-browser build/html/index.html

To check coverage:

    make coverage
    x-www-browser build/coverage/python.txt
