"""
Unit tests for customer endpoints
Coverage: CRUD operations, authentication, validation, edge cases
"""
import pytest
from fastapi import status


class TestCustomers:
    """Test customer management endpoints"""
    
    def test_get_customers_success(self, client, auth_headers, reset_data):
        """Test retrieving all customers with authentication"""
        response = client.get("/customers", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Alma"
    
    def test_get_customers_without_auth(self, client, reset_data):
        """Test that customers endpoint requires authentication"""
        response = client.get("/customers")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_customer_by_id_success(self, client, auth_headers, reset_data):
        """Test retrieving a specific customer"""
        response = client.get("/customers/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Alma"
        assert data["email"] == "Alma@example.com"
    
    def test_get_customer_by_id_not_found(self, client, auth_headers, reset_data):
        """Test retrieving non-existent customer"""
        response = client.get("/customers/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_customer_without_auth(self, client, reset_data):
        """Test that get customer by ID requires authentication"""
        response = client.get("/customers/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_customer_success(self, client, auth_headers, reset_data):
        """Test adding a new customer"""
        new_customer = {
            "name": "New Customer",
            "email": "new@example.com",
            "phone": "999-999-9999",
            "restrictions": [
                {"type": "Vegan", "description": "No animal products"}
            ],
            "goal": {
                "calories": 2200,
                "protein": 100,
                "carbs": 250,
                "fat": 70
            }
        }
        response = client.post("/customers", json=new_customer, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Customer"
        assert data["email"] == "new@example.com"
        assert data["id"] == 4
    
    def test_add_customer_without_optional_fields(self, client, auth_headers, reset_data):
        """Test adding customer with minimal required fields"""
        new_customer = {
            "name": "Minimal Customer",
            "email": "minimal@example.com",
            "goal": {
                "calories": 2000,
                "protein": 80,
                "carbs": 200,
                "fat": 60
            }
        }
        response = client.post("/customers", json=new_customer, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["phone"] == ""
        assert data["restrictions"] == []
    
    def test_add_customer_missing_required_fields(self, client, auth_headers, reset_data):
        """Test adding customer without required fields fails"""
        incomplete_customer = {
            "name": "Incomplete"
        }
        response = client.post("/customers", json=incomplete_customer, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_customer_without_auth(self, client, reset_data):
        """Test that adding customer requires authentication"""
        new_customer = {
            "name": "Test",
            "email": "test@test.com",
            "goal": {"calories": 2000, "protein": 80, "carbs": 200, "fat": 60}
        }
        response = client.post("/customers", json=new_customer)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_customer_success(self, client, auth_headers, reset_data):
        """Test updating an existing customer"""
        updated_data = {
            "name": "Alma Updated",
            "email": "alma.updated@example.com",
            "phone": "111-222-3333",
            "restrictions": [],
            "goal": {
                "calories": 1900,
                "protein": 85,
                "carbs": 210,
                "fat": 65
            }
        }
        response = client.put("/customers/1", json=updated_data, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Alma Updated"
        assert data["email"] == "alma.updated@example.com"
        assert data["goal"]["calories"] == 1900
    
    def test_update_customer_not_found(self, client, auth_headers, reset_data):
        """Test updating non-existent customer fails"""
        updated_data = {
            "name": "Ghost",
            "email": "ghost@example.com",
            "goal": {"calories": 2000, "protein": 80, "carbs": 200, "fat": 60}
        }
        response = client.put("/customers/999", json=updated_data, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_customer_without_auth(self, client, reset_data):
        """Test that updating customer requires authentication"""
        updated_data = {
            "name": "Test",
            "email": "test@test.com",
            "goal": {"calories": 2000, "protein": 80, "carbs": 200, "fat": 60}
        }
        response = client.put("/customers/1", json=updated_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_customer_success(self, client, auth_headers, reset_data):
        """Test deleting a customer"""
        response = client.delete("/customers/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        get_response = client.get("/customers/1", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_customer_not_found(self, client, auth_headers, reset_data):
        """Test deleting non-existent customer fails"""
        response = client.delete("/customers/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_customer_without_auth(self, client, reset_data):
        """Test that deleting customer requires authentication"""
        response = client.delete("/customers/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_customer_data_validation(self, client, auth_headers, reset_data):
        """Test that customer data types are validated"""
        invalid_customer = {
            "name": "Test",
            "email": "test@test.com",
            "goal": {
                "calories": "not_a_number",  # Should be int
                "protein": 80,
                "carbs": 200,
                "fat": 60
            }
        }
        response = client.post("/customers", json=invalid_customer, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_customer_restrictions_structure(self, client, auth_headers, reset_data):
        """Test that dietary restrictions have proper structure"""
        customer_with_restrictions = {
            "name": "Restricted User",
            "email": "restricted@example.com",
            "restrictions": [
                {"type": "Lactose Intolerant", "description": "Cannot consume dairy"},
                {"type": "Nut Allergy", "description": "Allergic to all nuts"}
            ],
            "goal": {"calories": 2100, "protein": 90, "carbs": 220, "fat": 68}
        }
        response = client.post("/customers", json=customer_with_restrictions, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["restrictions"]) == 2
        assert data["restrictions"][0]["type"] == "Lactose Intolerant"
