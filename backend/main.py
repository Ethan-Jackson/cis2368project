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

    #Example {
    #"title": "Girl with the polkadot dress",
    #"author": "Elton John",
    #"genre": "Horror",
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

@app.route('/api/library/customers', methods=['POST'])
def make_cust():
    data = request.get_json()
    fname = data['firstname']
    lname = data['lastname']
    email = data['email']
    unhashpassword = data['password']

    encoded = unhashpassword.encode() #unicode encoding
    hashedresult = hashlib.sha256(encoded) #hashing

    query = "INSERT INTO customers (firstname, lastname, email, passwordhash) VALUES ('%s', '%s', '%s', '%s')" % (fname, lname, email, passwordhash)
    execute_query(conn, query)
        
    return f'POSTED: {data}'

def dump_into_json(data):
    #Created to make everything more neat
    result = []
    for entry in data:
        #Adding each entry to the soon-to-be json
        result.append(entry)

    return jsonify(result)

app.run()