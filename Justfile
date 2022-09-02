set dotenv-load

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

fly:
    fly launch
    fly secrets import < .env
    fly deploy

refuel:
    fly secrets import < .env
    fly deploy

shoot-down:
    fly destroy gogostandup --yes