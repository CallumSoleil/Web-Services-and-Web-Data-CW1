from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "name")
    correct_password = secrets.compare_digest(credentials.password, "password")

    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return credentials.username