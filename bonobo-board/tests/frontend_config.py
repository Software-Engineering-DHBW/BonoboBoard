# -*- coding: utf-8 -*-

# default settings for local testing
DOMAIN   = "localhost"
PORT     = 80
PROTOCOL = "http"

# url
URL = "".join([PROTOCOL, "://", DOMAIN, ":", str(PORT)])

# application paths
APPLICATION_PATHS = [
    "/vorlesungsplan",
    "/leistungsuebersicht",
    "/email"
]

# import everything with *
__all__ = [
    "APPLICATION_PATHS",
    "DOMAIN",
    "PORT",
    "PROTOCOL",
    "URL"
]
