#!/usr/bin/env python3

import pymysql
from random import randint

user = {
    'user': 'shop_user',
    'password': 'shop123',
    'host': '127.0.0.1',
    'port': 3306
}


def load(invoice_count=100, product_limit=8):
    db = pymysql.Connect(**user)
    cur = db.cursor()
    sql = ("INSERT INTO shop.orders (customer_id, product_id, invoice_id)"
           "VALUES (%s, %s, %s)")

    rows = list()
    for i in range(0, invoice_count):
        invoice_id = i
        customer_id = randint(1, 20)
        products = randint(1, product_limit)
        for p in range(1, products + 1):
            product_id = p
            row = (customer_id, product_id, invoice_id)
            rows.append(row)
    print(rows)
    cur.executemany(sql, rows)
    db.commit()


if __name__ == "__main__":
    load()
