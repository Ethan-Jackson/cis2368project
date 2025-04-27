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
    print(data)

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

@app.route('/api/library/customers-books', methods=['GET'])
def get_cust_books():
    query = "SELECT * FROM customers"
    data = execute_read_query(conn, query)

    query = "SELECT * FROM books"
    data2 = execute_read_query(conn, query)

    return (data, data2)

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

@app.route('/api/library/customers/login', methods=['POST'])
def login_cust():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Hashing the password to compare
    encoded = password.encode()
    hashedresult = hashlib.sha256(encoded)

    query = "SELECT * FROM customers WHERE email = '%s' AND passwordhash = '%s'" % (email, hashedresult.hexdigest()[:45])
    customer_data = execute_read_query(conn, query)

    if len(customer_data) == 0:
        return jsonify({"error": "Invalid email or password"}), 401
    else:
        books_query = "SELECT * FROM books"
        books_data = execute_read_query(conn, books_query)

        customers_query = "SELECT * FROM customers"
        customers_data = execute_read_query(conn, customers_query)

        return jsonify({
            "message": "Login successful",
            "customer": customer_data[0],
            "books": books_data,
            "customers": customers_data
        })


@app.route('/api/library/borrow', methods=['POST'])
def make_borrow():
    data = request.get_json()
    print(data)
    book = data['bookid']
    cust = data['customerid']
    date_format = "%m/%d/%Y"
    borrow_date = datetime.datetime.today()

    query = "INSERT INTO borrowing_records (bookid, customerid, borrowdate) VALUES (%s, %s, '%s')" % (book, cust, borrow_date)
    execute_query(conn, query)

    query = "UPDATE books SET status = 'Checked Out' WHERE id = %s" % book
    execute_query(conn, query)
    return f'Created: {data}'

@app.route('/api/library/return', methods=['POST'])
def return_borrow():
    data = request.get_json()
    book = data['bookid']
    cust = data['customerid']
    date_format = "%m/%d/%Y"
    ret = datetime.datetime.today()

    query = "SELECT borrow_date FROM borrowingrecords WHERE bookid = %s AND customerid = %s" % (book, cust)
    borrowdata = execute_read_query(conn, query)
    borrow_date = borrowdata[0][0]

    late_fee = days_past_due(borrow_date)

    query = "UPDATE borrowingrecords SET (returndate, late_fee) = ('%s', %s) WHERE bookid = %s AND customerid = %s" % (ret, late_fee, book, cust)
    execute_query(conn, query)
    return f'Created: {data}'

@app.route('/api/library/borrow', methods=['GET'])
def check_borrow():
    query = "SELECT * FROM borrowingrecords"
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
    print(data)
    for entry in data:
        #Adding each entry to the soon-to-be json
        result.append(entry)

    return jsonify(result)

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