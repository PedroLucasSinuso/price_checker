# Evitar importações circulares
from sqlalchemy.orm import declarative_base

Base = declarative_base()