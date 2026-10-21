# Notes CRUD API

A no-frills REST-based API for managing basic notes.


## Installing

First create a Python virtual environment to isolate this project:

    python3 -m venv .venv

Then activate the virtual environment:

    source .venv/bin/activate

Then install the project's requiremnts:

    python3 -m pip install -r requirements.txt



## Running

    uvicorn main:app --reload


## Testing

### Manual

Please note that all these examples use port 11997, as port 8000 is not normally
free on my laptop.  &:|

#### Create a note

    curl -i http://localhost:11997/notes \
        -H "Content-Type: application/json" \
        -d '{ "title": "My first note", "text": "Hello, notes." }'

Example:

    $ curl -i http://localhost:11997/notes \
        -H "Content-Type: application/json" \
        -d '{ "title": "My first note", "text": "Hello, notes." }'
    HTTP/1.1 201 Created
    date: Tue, 20 Oct 2026 19:01:12 GMT
    server: uvicorn
    content-length: 55
    content-type: application/json

    {"id":8,"title":"My first note","text":"Hello, notes."}
    $

#### Read a note

    curl -i http://localhost:11997/notes/8

Example:

    $ curl -i http://localhost:11997/notes/8
    HTTP/1.1 200 OK
    date: Tue, 20 Oct 2026 19:04:37 GMT
    server: uvicorn
    content-length: 55
    content-type: application/json

    {"id":8,"title":"My first note","text":"Hello, notes."}
    $

#### Update a note

    curl -i http://localhost:11997/notes/8 \
        -X PATCH \
        -H "Content-Type: application/json" \
        -d '{ "text": "Hello again, notes." }'

Example:

    $ curl -i http://localhost:11997/notes/8 \
        -X PATCH \
        -H "Content-Type: application/json" \
        -d '{ "text": "Hello again, notes." }'
    HTTP/1.1 200 OK
    date: Tue, 20 Oct 2026 19:07:03 GMT
    server: uvicorn
    content-length: 61
    content-type: application/json

    {"id":8,"title":"My first note","text":"Hello again, notes."}
    $

#### Delete a note

    curl -i -X DELETE http://localhost:11997/notes/8

Example:

    $ curl -i -X DELETE http://localhost:11997/notes/8
    HTTP/1.1 200 OK
    date: Tue, 20 Oct 2026 19:08:37 GMT
    server: uvicorn
    content-length: 26
    content-type: application/json

    {"message":"Note deleted"}
    $

#### Read a non-existent note

    curl -i http://localhost:11997/notes/8

Example:

    $ curl -i http://localhost:11997/notes/8
    HTTP/1.1 404 Not Found
    date: Tue, 20 Oct 2026 19:10:02 GMT
    server: uvicorn
    content-length: 27
    content-type: application/json

    {"detail":"Note not found"}
    $

### Automated

To run all the unit tests, simply:

    pytest -v --cov
