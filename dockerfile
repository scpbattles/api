FROM python:3

WORKDIR /usr/src/scpbattlesapi

COPY ./src/scpbattlesapi/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/scpbattlesapi .

CMD [ "python", "-m", "scpbattlesapi" ]
