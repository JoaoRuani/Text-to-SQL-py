# DB Chat

DB Chat is a web application that allows users to interact with databases using natural language. It provides a user-friendly interface for managing database connections and executing SQL queries through AI-powered natural language processing.

## Features

- User authentication (login/register)
- Secure storage of database connection strings
- Support for multiple database types (PostgreSQL, MySQL, SQL Server, Oracle)
- AI-powered SQL query generation from natural language
- Real-time query execution and results display
- Connection string management per user

## Prerequisites

### Docker Setup
- Docker and Docker Compose
- NVIDIA GPU (optional, for better AI performance)
- Git

### Local Setup
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Ollama (for AI capabilities)
- Git
- Virtual environment (recommended)

## Installation

### Docker Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/dbchat.git
cd dbchat
```

2. Create a `.env` file in the root directory with the following content:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/dbchat
SECRET_KEY=your-secret-key-here
API_BASE_URL=http://localhost:8000
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=llama3.2
```

Replace `your-secret-key-here` with a secure random string for JWT token generation.

### Local Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/dbchat.git
cd dbchat
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install and start Ollama:
```bash
# Follow instructions at https://ollama.ai/download
# Then pull the model
ollama pull llama3.2
```

5. Set up PostgreSQL:
```bash
# Create database
createdb dbchat

# Create .env file
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dbchat
SECRET_KEY=your-secret-key-here
API_BASE_URL=http://localhost:8000
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=llama3.2" > .env
```

6. Initialize the database:
```bash
# Run the initialization script
psql -U postgres -d dbchat -f db/init.sql
```

## Running the Application

### Docker Setup
1. Start the services using Docker Compose:
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database
- Ollama AI service
- FastAPI backend
- Streamlit frontend

2. Access the application:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

### Local Setup
1. Start the Ollama service (if not already running):
```bash
ollama serve
```

2. In a new terminal, start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

3. In another terminal, start the Streamlit frontend:
```bash
streamlit run app/frontend.py
```

4. Access the application:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

## Development

### Docker Development
To modify the application:

1. Make changes to the source code
2. Rebuild the containers:
```bash
docker-compose up --build
```

### Local Development
1. Make changes to the source code
2. The FastAPI server will automatically reload
3. For frontend changes, Streamlit will automatically update

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT token secret key
- `API_BASE_URL`: Backend API URL
- `OLLAMA_ENDPOINT`: Ollama service URL
- `OLLAMA_MODEL`: AI model to use (default: llama3.2)
