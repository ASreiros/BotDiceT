FROM python:3.11.4-slim-bullseye
# sukelia iš source į docker/app
COPY . /main
WORKDIR /main
RUN pip install -r requirements.txt
ENTRYPOINT python3 main.py