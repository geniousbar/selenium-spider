# -*- coding:utf-8 -*-
from orator import DatabaseManager

config = {
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'my1688',
        'user': 'root',
        'password': 'sun',
        'prefix': ''
    }
}

db = DatabaseManager(config)
