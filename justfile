# host a webserver
host:
    python -m http.server

# generate graph.json for target
generate target:
    python ./nid/main.py {{target}}

install:
    pip install -r requirements.txt -r requirements-dev.txt
    pre-commit install
