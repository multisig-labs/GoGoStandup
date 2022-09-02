FROM python:3.10

WORKDIR /app

RUN pip3 install -U pip pipenv
COPY . /app

RUN pipenv install --system

CMD ["python3", "bot.py"]
