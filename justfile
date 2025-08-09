# Default: show available commands
_default:
    just --list

# Host a webserver for testing vis
webs:
    ./venv/bin/python -m http.server

# Generate graph.json for target
build *targets:
   python -m nid.nid -o ./out/graph.json {{targets}}

# Install project dependencies using venv
install:
    test -d venv || python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt -r requirements-dev.txt
    ./venv/bin/pre-commit install
    mkdir -p ./lib
    cd ./lib && curl -O https://d3js.org/d3.v7.js

# Setup: install and prep everything
setup: install
    echo "Project setup done."
    echo "Now run: source venv/bin/activate"
