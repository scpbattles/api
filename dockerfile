FROM python:3

WORKDIR /usr/src/app

# install requirements
COPY ./src/scpbattlesapi/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# make module folder
RUN mkdir scpbattlesapi

# copy contents of the module to the module folder in container
COPY ./src/scpbattlesapi ./scpbattlesapi

# copy config files
RUN mkdir /etc/scpbattlesapi
COPY config.yaml /etc/scpbattlesapi
COPY bad_words.json /etc/scpbattlesapi

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "scpbattlesapi.app:app"]
