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
RUN mkdir -p /usr/local/share/scpbattlesapi/wallpapers
COPY config.yaml /etc/scpbattlesapi
COPY bad_words.json /etc/scpbattlesapi 
COPY wallpapers /usr/local/share/scpbattlesapi/wallpapers

# install mongosh
RUN wget "https://downloads.mongodb.com/compass/mongodb-mongosh_1.10.5_amd64.deb"
RUN dpkg -i "mongodb-mongosh_1.10.5_amd64.deb"

# copy database init script
COPY database_init.sh .  

# copy startup script
COPY docker_startup.sh .

CMD ["/bin/bash", "docker_startup.sh"]
