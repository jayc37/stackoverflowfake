FROM python:3.7-alpine

ENV FLASK_APP run.py
ENV FLASK_CONFIG production

WORKDIR /stackoverflow

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY run.py config.py boot.sh ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
