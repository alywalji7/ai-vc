import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from main import app, get_db

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Polyglot Monorepo Backend API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_user():
    response = client.post(
        "/api/users/",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    
    # Clean up created user for other tests
    user_id = data["id"]
    return user_id

def test_create_duplicate_user():
    # First, create a user
    client.post(
        "/api/users/",
        json={"username": "duplicate", "email": "duplicate@example.com", "password": "password123"},
    )
    
    # Attempt to create a duplicate username
    response = client.post(
        "/api/users/",
        json={"username": "duplicate", "email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    
    # Attempt to create a duplicate email
    response = client.post(
        "/api/users/",
        json={"username": "newuser", "email": "duplicate@example.com", "password": "password123"},
    )
    assert response.status_code == 400

def test_read_users():
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_create_and_read_item():
    # First, create a user
    user_response = client.post(
        "/api/users/",
        json={"username": "itemuser", "email": "itemuser@example.com", "password": "password123"},
    )
    user_id = user_response.json()["id"]
    
    # Create an item for the user
    item_response = client.post(
        f"/api/users/{user_id}/items/",
        json={"title": "Test Item", "description": "This is a test item"},
    )
    assert item_response.status_code == 200
    item_data = item_response.json()
    assert item_data["title"] == "Test Item"
    assert item_data["owner_id"] == user_id
    
    # Get all items
    items_response = client.get("/api/items/")
    assert items_response.status_code == 200
    items = items_response.json()
    assert len(items) > 0
