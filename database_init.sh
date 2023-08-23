#!/bin/bash
mongosh <<HERE
use scpbattles
db.createCollection("users")
db.createCollection("servers")
db.createCollection("itemgiftcards")
HERE