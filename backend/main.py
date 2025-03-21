import time
import hashlib
import datetime

import flask
from flask import jsonify
from flask import request

from credas import Creds

import mysql.connector
from mysql.connector import Error
from sql import (create_con, execute_query, execute_read_query)


mycreds = Creds()
conn = create_con(mycreds.conString, mycreds.userName, mycreds.password, mycreds.dbName)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/library/books', methods=['GET'])
def get_inventory():
    #Getting all entries
    query = "SELECT * FROM books"

    #Keeping it clean
    data = execute_read_query(conn, query)

    return dump_into_json(data)

@app.route('/api/library/books', methods=['POST'])
def new_book():

    #{
    #"title": "Hitchhikers Guide to the Galaxy",
    #"author": "Douglas Adams",
    #"genre": "Science Fiction",
    #"status": "Available"
    #}

    #Getting data form user
    data = request.get_json()
    title = data['title']
    author = data['author']
    genre = data['genre']

    try:
        status = data['status']
    except:
        status = "Available"


    query = "INSERT INTO books (title, author, genre, status) VALUES ('%s', '%s', '%s', '%s')" % (title, author, genre, status)
    execute_query(conn, query)
        
    return f'POSTED: {data}'

@app.route('/api/library/books', methods=['PUT'])
def update_book():
    #Example {
    #    "id": 7,
    #    "owner": "Jeff Bezos",
    #    "value": "$1,250,060"
    #}

    #Getting data form user
    data = request.get_json()
    bookid = data['id']

    for key in data:
        if key == 'id':
            pass
        else:
            query = "UPDATE books SET %s = '%s' WHERE id = %s" % (key, data[key], int(bookid))
            execute_query(conn, query)

    return f'Updated: {data}'

@app.route('/api/library/books', methods=['DELETE'])
def delete_book():

    data = request.get_json()
    bookid = data['id']

    query = "DELETE from books WHERE id = '%s'" % (bookid)

    return f'Deleted: {data}'

@app.route('/api/library/customers', methods=["GET"])
def get_cust():
    query = "SELECT * FROM customers"
    data = execute_read_query(conn, query)

    return dump_into_json(data)


#{
#    "firstname": "Ethan",
#    "lastname": "Jackson",
#    "email": "eajacks5@cougarnet.uh.edu",
#    "password": "password"
#}

@app.route('/api/library/customers', methods=['POST'])
def make_cust():
    data = request.get_json()
    fname = data['firstname']
    lname = data['lastname']
    email = data['email']
    unhashpassword = data['password']

    encoded = unhashpassword.encode() #unicode encoding
    hashedresult = hashlib.sha256(encoded) #hashing

    query = "INSERT INTO customers (firstname, lastname, email, passwordhash) VALUES ('%s', '%s', '%s', '%s')" % (fname, lname, email, hashedresult.hexdigest())
    execute_query(conn, query)
        
    return f'POSTED: {data}'

@app.route('/api/library/customers', methods=['PUT'])
def edit_cust():
    data = request.get_json()
    cust_id = data['id']

    for key in data:
        if key == 'id':
            pass
        else:
            if key == 'password':
                encoded = data[key].encode() #unicode encoding
                hashedresult = hashlib.sha256(encoded) #hashing
                query = "UPDATE customers SET passwordhash = '%s' WHERE id = %s" % (hashedresult.hexdigest(), int(cust_id))
                execute_query(conn, query)
            else:
                query = "UPDATE customers SET %s = '%s' WHERE id = %s" % (key, data[key], int(cust_id))
                execute_query(conn, query)

    return f'Updated: {data}'

@app.route('/api/library/customers', methods=['DELETE'])
def delete_cust():
    data = request.get_json()
    cust_id = data['id']

    query = "DELETE from customers WHERE id = %s" % cust_id
    execute_query(conn, query)
    return f'Deleted: {data}'

@app.route('/api/library/borrow', methods=['POST'])
def make_borrow():
    data = request.get_json()
    book = data['bookid']
    cust = data['customerid']
    borrow_date = data['borrow_date']
    return_date = data['return_date']

    query = "INSERT INTO borrow_records (bookid, customerid, borrow_date, return_date) VALUES (%s, %s, '%s', '%s')" % (book, cust, borrow_date, return_date)
    execute_query(conn, query)
    return f'Created: {data}'

@app.route('/api/library/borrow', methods=['GET'])
def check_borrow():
    query = "SELECT * FROM borrow_records"
    data = execute_read_query(conn, query)

    return data

#}
#    "bookid": 1,
#   "customerid": 1,
#   "borrow_date": "3/17/2025",
#    "return_date": "3/24/2025"
#}
@app.route('/api/library/borrow', methods=['PUT'])
def edit_borrow():
    data = request.get_json()
    borrowid = data['id']

    for key in data:
        if key == 'id':
            pass
        else:
            query = "UPDATE borrow_records SET %s = '%s' WHERE id = %s" % (key, data[key], int(bookid))
            execute_query(conn, query)

    return f'Updated: {data}'

@app.route('/api/library/borrow', methods=['DELETE'])
def delete_borrow():
    data = request.get_json()
    borrowid = data['id']

    query = "DELETE FROM borrow_records WHERE id = %s" % borrowid
    execute_query(conn, query)

    return f'Deleted: {data}'

def dump_into_json(data):
    #Created to make everything more neat
    result = []
    for entry in data:
        #Adding each entry to the soon-to-be json
        result.append(entry)

def days_past_due(date):

    #To be used in the future to calculate the days past a certain date
    #Credit: https://stackoverflow.com/questions/32490629/getting-todays-date-in-yyyy-mm-dd-in-python
    #and
    #https://stackoverflow.com/questions/151199/how-to-calculate-number-of-days-between-two-given-dates

    date_format = "%m/%d/%Y"
    today = datetime.datetime.today()
    print(today)
    comp = datetime.datetime.strptime(date, date_format)
    diff = today - comp
    print(diff.days)

    return jsonify(result)

app.run()