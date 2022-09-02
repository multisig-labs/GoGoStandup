default:
    just --list

install:
    python3 -m pip install -U pip pipenv
    pipenv install

build-docker:
    docker build -t multisig-labs/gogostandup:latest .

run-docker:
    docker run --env-file .env multisig-labs/gogostandup:latest

run:
    pipenv run python3 bot.py