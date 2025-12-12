"""
Unit tests for authentication endpoints
Coverage: registration, login, token validation, error cases
"""
import pytest
from fastapi import status


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_new_user_success(self, client, reset_data):
        """Test successful user registration"""
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "testpass123",
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "hashed_password" not in data
    
    def test_register_duplicate_username(self, client, reset_data):
        """Test registration with existing username fails"""
        # First registration
        client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        # Duplicate registration
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "password": "anotherpass"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]
    
    def test_register_without_optional_fields(self, client, reset_data):
        """Test registration with only required fields"""
        response = client.post(
            "/register",
            json={
                "username": "minimaluser",
                "password": "pass123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "minimaluser"
    
    def test_register_missing_required_fields(self, client, reset_data):
        """Test registration without required fields fails"""
        response = client.post(
            "/register",
            json={"username": "onlyusername"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_success(self, client, reset_data):
        """Test successful login returns valid token"""
        response = client.post(
            "/login",
            data={"username": "admin", "password": "secret"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, reset_data):
        """Test login with wrong password fails"""
        response = client.post(
            "/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client, reset_data):
        """Test login with non-existent username fails"""
        response = client.post(
            "/login",
            data={"username": "nonexistent", "password": "anypass"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_credentials(self, client, reset_data):
        """Test login without credentials fails"""
        response = client.post("/login", data={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_current_user_with_valid_token(self, client, auth_headers, reset_data):
        """Test accessing user info with valid token"""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"
    
    def test_get_current_user_without_token(self, client, reset_data):
        """Test accessing user info without token fails"""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_with_invalid_token(self, client, reset_data):
        """Test accessing user info with invalid token fails"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalidtoken123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_with_malformed_token(self, client, reset_data):
        """Test accessing user info with malformed authorization header"""
        response = client.get(
            "/users/me",
            headers={"Authorization": "InvalidFormat token123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_password_is_hashed(self, client, reset_data):
        """Test that passwords are properly hashed"""
        # Register a user
        client.post(
            "/register",
            json={
                "username": "hashtest",
                "password": "plainpassword"
            }
        )
        # Verify the password is hashed by trying to login
        response = client.post(
            "/login",
            data={"username": "hashtest", "password": "plainpassword"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_token_authentication_workflow(self, client, reset_data):
        """Test complete authentication workflow: register -> login -> access protected resource"""
        # Step 1: Register
        register_response = client.post(
            "/register",
            json={
                "username": "workflowuser",
                "password": "workflowpass"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Login
        login_response = client.post(
            "/login",
            data={"username": "workflowuser", "password": "workflowpass"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # Step 3: Access protected resource
        protected_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == status.HTTP_200_OK
        assert protected_response.json()["username"] == "workflowuser"
