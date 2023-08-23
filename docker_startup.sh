#!/bin/bash
source database_init.sh

gunicorn -b 0.0.0.0:5000 scpbattlesapi.app:app