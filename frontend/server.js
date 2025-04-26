//Load Express Module
const express = require('express')
const path = require('path')
const alert = require('alert-node')
const axios = require('axios');

//Put the express Apllication insid ethe app variable
const app = express()

app.use(express.urlencoded({ extended: true }));

//Set views property and view engine
app.set("views", path.resolve(__dirname, "views"))
app.set("view engine", "ejs")

const port = 8080

var user_id = 0;

//When the user asks for home page, then the message should show in the browser

app.get('/', (request, response) => response.render('hello', {
    result: null
}));

app.get('/login', (request, response) => response.render('login'));

app.post('/login', (request, response) => {
    //console.log(request.body.email, request.body.password);
    axios.post('http://127.0.0.1:5000/api/library/customers/login', { 
        "email": request.body.email,
        "password": request.body.password
    })
    .then(function (res) {
        //console.log(res.data);
        alert('Login successful! Welcome to the library.');
        //console.log(res.data.customer['id']);
        id = res.data.customer['id'];
        user_id = id;
        axios.get('http://127.0.0.1:5000/api/library/customers/')
        .then(function (res) {
            const customers = res.data;
        });
        axios.get('http://127.0.0.1:5000/api/library/books')
        .then(function (res) {
            //console.log(res.data);
            response.render('useractions', {
                user_id: id,
                books: res.data,
                customers: customers
            });
        })
    })
    .catch(function (error) {
        //console.log(error);
        alert('Login failed! Try again.');
    })
});

app.post('/books/update', (request, response) => {
    axios.put('http://127.0.0.1:5000/api/library/books', {
        id: request.body.book_id,
        genre: request.body.new_genre
    })
    .then(function (res) {
        alert('Book updated successfully!');
        response.redirect('/');
    })
    .catch(function (error) {
        console.log(error);
        alert('Failed to update book.');
    });
});

app.post('/books/delete', (request, response) => {
    axios.delete('http://127.0.0.1:5000/api/library/books', {
        data: { id: request.body.book_id }
    })
    .then(function (res) {
        alert('Book deleted successfully!');
        response.redirect('/');
    })
    .catch(function (error) {
        console.log(error);
        alert('Failed to delete book.');
    });
});

app.post('/register', (request, response) => {
    axios.post('http://127.0.0.1:5000/api/library/customers', { 
        "firstname": request.body.firstname,
        "lastname": request.body.lastname,
        "email": request.body.email,
        "password": request.body.password
    })
    .then(function (response) {
        alert('Registration successful! Check your email for verification.');
    })
    .catch(function (error) {
        console.log(error);
        alert('Registration failed! Try again.');
    });
});

app.post('/useractions', (request, response) => {
    console.log(user_id);
    console.log(request.body.book_id);
    axios.post('http://127.0.0.1:5000/api/library/borrow', {
        "bookid": request.body.book_id,
        "customerid": user_id
    })
    .then(function (res) {
        //console.log(res.data);
        alert('Book borrowed successfully!');
    })

});


app.get('/books', (request, response) => {
    axios.get('http://127.0.0.1:5000/api/library/books')
        .then(function (res) {
            response.render('books', {
                books: res.data
            });
        })
        .catch(function (error) {
            console.log(error);
            response.send('Error retrieving books.');
        });
});

app.post('/books', (request, response) => {
    const method = request.body._method;
    const data = {
        id: request.body.id,
        title: request.body.title,
        author: request.body.author,
        genre: request.body.genre,
        status: request.body.status
    };

    if (method === 'POST') {
        // Add new book
        axios.post('http://127.0.0.1:5000/api/library/books', {
            title: data.title,
            author: data.author,
            genre: data.genre,
            status: data.status
        })
        .then(res => {
            response.redirect('/books');
        })
        .catch(error => {
            console.log(error);
            response.send('Error adding book.');
        });
    } 
    else if (method === 'PUT') {
        // Update book
        axios.put('http://127.0.0.1:5000/api/library/books', {
            id: data.id,
            title: data.title,
            author: data.author,
            genre: data.genre,
            status: data.status
        })
        .then(res => {
            response.redirect('/books');
        })
        .catch(error => {
            console.log(error);
            response.send('Error updating book.');
        });
    }
    else if (method === 'DELETE') {
        // Delete book
        axios.delete('http://127.0.0.1:5000/api/library/books', {
            data: { id: data.id }
        })
        .then(res => {
            response.redirect('/books');
        })
        .catch(error => {
            console.log(error);
            response.send('Error deleting book.');
        });
    }
});

//Start the express application on port 8080
app.listen(port, () => console.log('Listening on port 8080'))
