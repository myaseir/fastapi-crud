from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from schemas import User, UserCreate, ManualRegisterCreate, RegisterOut


import crud
import registration
from db import get_connection
import bcrypt

app = FastAPI()

# ------------------ Dependency ------------------
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# ------------------ Google Auth Registration ------------------
@app.post("/register-google-user/", response_model=User)
def register_google_user(user: UserCreate, conn=Depends(get_db)):
    created_user = crud.create_user_if_not_exists(conn, user)
    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
    return created_user

# ------------------ Manual User CRUD ------------------
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, conn=Depends(get_db)):
    return crud.create_user(user)

@app.get("/users/", response_model=list[User])
def read_all_users(conn=Depends(get_db)):
    return crud.get_users()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: str, conn=Depends(get_db)):
    user = crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: UserCreate, conn=Depends(get_db)):
    updated = crud.update_user(user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: str, conn=Depends(get_db)):
    deleted = crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted

# ------------------ Registration Table ------------------

@app.post("/register", response_model=RegisterOut)
def register_user(user: ManualRegisterCreate, conn=Depends(get_db)):

    return registration.create_registration(conn, user)

@app.get("/register", response_model=list[RegisterOut])
def list_registered_users(conn=Depends(get_db)):
    return registration.get_all_registrations(conn)

# ------------------ Manual Login ------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login_user(login: LoginRequest, conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM register WHERE email = %s", (login.email,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        stored_hash = user["password_hash"]
        if not bcrypt.checkpw(login.password.encode(), stored_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {"id": user["id"], "email": user["email"]}

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
