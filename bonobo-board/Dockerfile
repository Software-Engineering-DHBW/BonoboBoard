FROM python:3.9

SHELL ["/bin/bash", "-c"]

# set workdir
WORKDIR /bonobo-board

#
COPY . .

# remove unwanted files
RUN rm -rf CHANGELOG.md \
    docker-compose.yml \
    Dockerfile \
    LICENSE.md \
    nginx/ \
    README.md

#RUN mv python_inc_bonobo_modules.sh /etc/profile.d/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /bonobo-board/modules

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r ./modules/dhbw/requirements.txt

# running migrations
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

# gunicorn
#CMD ["/bin/bash", "-c", "source /etc/profile.d/python_inc_bonobo_modules.sh && gunicorn --config gunicorn-cfg.py core.wsgi"]
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
