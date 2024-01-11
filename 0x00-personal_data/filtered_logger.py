#!/usr/bin/env python3
"""
data filtration and logging
"""
import logging
import mysql.connector
import os
import re
from typing import List
PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    '''filter and censor data'''
    if not message:
        return fields

    for i in fields:
        pattern = i + r'=.*?' + separator
        replacement = f'{i}={redaction}{separator}'
        message = re.sub(pattern, replacement, message)
    return message


def get_logger() -> logging.Logger:
    '''return logging.logger object'''
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handle = logging.StreamHandler()
    handle.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(handle)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    '''set up db connection'''
    return mysql.connector.connection.MySQLConnection(
            host=os.environ.get('PERSONAL_DATA_DB_HOST', 'localhost'),
            user=os.environ.get('PERSONAL_DATA_DB_USERNAME', 'root'),
            password=os.environ.get('PERSONAL_DATA_DB_PASSWORD', ""),
            database=os.environ.get('PERSONAL_DATA_DB_NAME')
            )


def main():
    '''logging db data'''
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for row in cursor:
        data = ''.join([f'{title[0]}={entry}; ' for title, entry
                        in zip(cursor.description, row)])
        logger.info(data.strip())
    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        '''formatter init'''
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        ''' format and filter text'''
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super().format(record)


if __name__ == "__main__":
    main()
