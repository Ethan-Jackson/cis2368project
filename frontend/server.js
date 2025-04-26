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

//When the user asks for home page, then the message should show in the browser

app.get('/', (request, response) => response.render('hello', {
    result: null
}));

app.get('/login', (request, response) => response.render('login'));

app.post('/login', (request, response) => {
    console.log(request.body.email, request.body.password);
    axios.post('http://127.0.1:5000/api/library/customers/login', { 
        "email": request.body.email,
        "password": request.body.password
    })
    .then(function (response) {
        if (response.data.status == 'success') {
            alert('Login successful!');
            response.render('hello', { result: response.data });
        } else {
            alert('Login failed! Check your email and password.');
            response.render('login');
        }
    })
    .catch(function (error) {
        console.log(error);
        alert('Login failed! Try again.');
    })
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

//Start the express application on port 8080
app.listen(port, () => console.log('Listening on port 8080'))
