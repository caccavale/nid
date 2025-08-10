venv := ".venv"

_venv_bin_dir := if os_family() == "windows" { "Scripts" } else { "bin" }
_venv_loc := venv / _venv_bin_dir / "activate"
_source := "source " + _venv_loc + " &&"

_default:
    just --list

# host a webserver for testing vis
webs:
    {{_source}} cd ./niddy && python -m http.server

# generate graph.json for target (`just build --help` for more info)
build *targets:
    {{_source}} python -m nid.nid -o ./niddy/out/graph.json {{targets}}

# install project dependencies
install: _venv _lib

_lib:
    mkdir -p ./lib
    cd ./lib && curl -O https://d3js.org/d3.v7.js

_venv:
    pip install virtualenv
    python -m venv {{venv}}
    {{_source}} pip install -r requirements.txt -r requirements-dev.txt
    {{_source}} pre-commit install

clean:
    rm -rf ./cache