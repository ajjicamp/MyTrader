import sqlite3
import pandas as pd
from PyQt5.QtGui import QFont, QColor
import os

OPENAPI_PATH = 'C:/OpenAPI'
SYSTEM_PATH = os.path.dirname(os.path.dirname(__file__))
DB_STG = f'{SYSTEM_PATH}/database/stg.db'

scrNo = {}
scrNo['TR조회'] = 1000
scrNo['장운영시간'] = 1003
scrNo['실시간종목'] = 2000
scrNo['조건검색식'] = 3000

