#!/bin/bash

FAILURE=1
SUCCESS=0

### ROOT PRIVILEGES NEEDED

if [ `id -u` -ne 0 ]; then
        >&2 echo -e "\033[1;31mScript needs root privileges.\nRun with sudo, su or as root!\033[0m"
        exit
fi

function exit_on_error {
	if [ `$?` -ne 0 ]; then
		echo "An error appeared, aborting container creation"
		exit $FAILURE
}

echo "Starting the Docker Containers ..."
docker-compose up -d appseed-app
exit_on_error
docker-compose up -d nginx
exit_on_error
echo "Docker Container are successfully deployed!"
exit $SUCCESS
