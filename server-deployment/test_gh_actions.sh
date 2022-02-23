#!/bin/bash
echo "Deploying on VPS..."
cd /srv/
git checkout main
git pull
cd /srv/bonobo-board
docker-compose up -d #@JH insert docker-compose prod logic here
echo "Deployed!"
