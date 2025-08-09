_default:
    just --list

# host a webserver for testing vis
webs:
    python -m http.server

# generate graph.json for target (`just build --help` for more info)
build *targets:
    python ./nid/main.py -o ./out/graph.json {{targets}}

# install project dependencies
install:
    pip install -r requirements.txt -r requirements-dev.txt
    pre-commit install
    mkdir -p ./lib
    cd ./lib && curl -O https://d3js.org/d3.v7.js
