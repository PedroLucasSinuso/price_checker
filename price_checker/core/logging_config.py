import logging
from logging.config import dictConfig

def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            },
            "etl": {
                "format": "%(asctime)s [ETL] [%(levelname)s] %(message)s",
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file_app": {
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "formatter": "default",
            },
            "file_etl": {
                "class": "logging.FileHandler",
                "filename": "logs/etl.log",
                "formatter": "etl",
            },
        },

        "loggers": {
            "price_checker": {
                "level": "INFO",
                "handlers": ["console", "file_app"],
                "propagate": False,
            },
            "price_checker.etl": {
                "level": "INFO",
                "handlers": ["console", "file_etl"],
                "propagate": False,
            },
        },

        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    })