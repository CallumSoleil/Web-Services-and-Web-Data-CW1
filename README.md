# Football API
A FastAPI application that provides statistics for players and teams throughout an ongoing football season. The API includes analytical tools to assess current player and team form, as well as simple match prediction functionality. A SQLite database stores players, teams, matches, and performance records, all accessible through standard HTTP requests.
Full API documentation is generated using FastAPI ReDoc and is available in the repository as “FastAPI – ReDoc.pdf”, and also via the /redoc endpoint when running the server.

## Authentification
User authentication is required for all requests that modify the database (Create, Update, Delete).
- Username: name
- Password: password
All read‑only GET requests are publicly accessible.


## Setup Instructions
git clone <https://github.com/CallumSoleil/Web-Services-and-Web-Data-CW1>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload