# FastAPI CRUD with PostgreSQL

This is a simple FastAPI project for doing CRUD (Create, Read, Update, Delete) operations using PostgreSQL.

## 📦 Features

- Create new items  
- Read all items or single item by ID  
- Update items  
- Delete items  

## 🛠 Tech Stack

- FastAPI  
- PostgreSQL  
- SQLAlchemy (ORM)  
- Pydantic  

## 🚀 Setup & Run

Clone this repo  
   ```bash
   git clone https://github.com/myaseir/fastapi-crud.git
   cd fastapi-crud

Install dependencies

bash
Copy code
pip install -r requirements.txt

Create a .env file and set your database URL

bash
Copy code
DATABASE_URL=postgresql://username:password@localhost:5432/your_db

Run the app

bash
Copy code
uvicorn main:app --reload

📄 API Docs
Go to http://127.0.0.1:8000/docs for Swagger UI interface.
