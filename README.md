# API Edu - Management API

This project provides an API for managing data, allowing clients to fetch  information about **edu.azores**. Currently, the API includes an endpoint to retrieve a list of schools.



## Introduction

API Edu is a web-based project that offers a backend API to manage educational data. It is designed to provide an easy-to-use interface for managing and retrieving information through RESTful API calls. The API requires an API key for authentication, ensuring that only authorized users can access the data.

## Technologies Used

- **Python 3**
- **Flask** - Web framework for Python
- **PyMySQL** - Database connector for MySQL
- **bcrypt** - Password hashing for authentication
- **HTML/CSS/JavaScript** - Frontend for displaying data (in progress)

## API Endpoints

### `GET /escolas`

Retrieves a list of all schools in the database.

#### Response
```json
{
    "table": [
        [1, "Escola A", 101],
        [2, "Escola B", 102],
        [3, "Escola C", 103]
    ]
}
```
#### Authentication
The API requires an API key for authentication. The API key must be sent in the request header as X-API-KEY.
```bash
curl -H "X-API-KEY: your_api_key_here" http://localhost:5000/escolas

```

## Contributing

Contributions to the project are welcome! 
License

## This project is licensed under the MIT License - see the LICENSE file for details.
