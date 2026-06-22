import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2 import errors
from dotenv import load_dotenv

# Load cloud database URL
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="AI Engineering Weekly API")

class SubscriberRequest(BaseModel):
    email: EmailStr

# Serve the HTML frontend
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

# Handle the subscription logic
@app.post("/subscribe")
def subscribe_user(request: SubscriberRequest):
    try:
        # Connect to Neon Cloud DB
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO subscribers (email) VALUES (%s);
        """
        cursor.execute(insert_query, (request.email,))
        conn.commit()
        
        return {"message": "Successfully Subscribed!"}
        
    except errors.UniqueViolation:
        if 'conn' in locals(): conn.rollback()
        return {"message": "You are already subscribed!"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()