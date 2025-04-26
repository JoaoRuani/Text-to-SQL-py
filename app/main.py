from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import timedelta

from app.ai.mistral import MistralAIService

from .supportedDBs.manager import DatabaseManagerService
from .ai.ollama import OllamaAIService
from . import models, schemas, auth
from .database import engine, get_db

# Load environment variables
load_dotenv()

app = FastAPI(title="DBChat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_manager = DatabaseManagerService()
# ai_service = OllamaAIService({
#     "ollama_endpoint": os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
#     "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2")
# })

ai_service = MistralAIService({
    "mistral_api_key": os.getenv("MISTRAL_KEY"),
    "mistral_model": os.getenv("MISTRAL_MODEL", "mistral-large-latest")
})

models.Base.metadata.create_all(bind=engine)

class ConnectionRequest(BaseModel):
    db_type: str
    connection_string: str

class QueryRequest(BaseModel):
    natural_language: str

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    token_request: schemas.TokenRequest,
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, token_request.username, token_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/connection-strings/", response_model=schemas.ConnectionString)
def create_connection_string(
    connection_string: schemas.ConnectionStringCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_connection_string = models.ConnectionString(
        **connection_string.dict(),
        user_id=current_user.id
    )
    db.add(db_connection_string)
    db.commit()
    db.refresh(db_connection_string)
    return db_connection_string

@app.get("/connection-strings/", response_model=list[schemas.ConnectionString])
def read_connection_strings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.ConnectionString).filter(
        models.ConnectionString.user_id == current_user.id
    ).all()

@app.get("/connection-strings/{connection_string_id}", response_model=schemas.ConnectionString)
def read_connection_string(
    connection_string_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    connection_string = db.query(models.ConnectionString).filter(
        models.ConnectionString.id == connection_string_id,
        models.ConnectionString.user_id == current_user.id
    ).first()
    if connection_string is None:
        raise HTTPException(status_code=404, detail="Connection string not found")
    return connection_string

@app.delete("/connection-strings/{connection_string_id}")
def delete_connection_string(
    connection_string_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    connection_string = db.query(models.ConnectionString).filter(
        models.ConnectionString.id == connection_string_id,
        models.ConnectionString.user_id == current_user.id
    ).first()
    if connection_string is None:
        raise HTTPException(status_code=404, detail="Connection string not found")
    db.delete(connection_string)
    db.commit()
    return {"message": "Connection string deleted successfully"}

@app.post("/connect")
async def connect(request: ConnectionRequest):
    try:
        service = db_manager.get_service(request.db_type)
        await service.connect(request.connection_string)
        return {"message": "Connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/disconnect")
async def disconnect():
    try:
        service = db_manager.get_current_service()
        await service.disconnect()
        return {"message": "Disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/schema")
async def get_schema():
    try:
        service = db_manager.get_current_service()
        schema = await service.get_schema()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/query")
async def execute_query(request: QueryRequest):
    try:
        service = db_manager.get_current_service()
        schema = await service.get_schema()
        
        # Generate SQL query using AI
        sql_query = await ai_service.generate_sql_query(request.natural_language, schema, service.database_type)
        
        # Execute the query
        results = await service.execute_query(sql_query)
        
        return {
            "sql_query": sql_query,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 