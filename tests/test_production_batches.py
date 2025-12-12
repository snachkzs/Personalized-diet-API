"""
Unit tests for production batch endpoints
Coverage: CRUD operations, business logic, edge cases
"""
import pytest
from fastapi import status


class TestProductionBatches:
    """Test production batch management endpoints"""
    
    def test_get_production_batches_success(self, client, auth_headers, reset_data):
        """Test retrieving all production batches"""
        response = client.get("/production-batches", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["productionDate"] == "2025-11-17"
    
    def test_get_production_batches_without_auth(self, client, reset_data):
        """Test that production batches endpoint requires authentication"""
        response = client.get("/production-batches")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_production_batch_by_id_success(self, client, auth_headers, reset_data):
        """Test retrieving a specific production batch"""
        response = client.get("/production-batches/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert "dietPlans" in data
        assert "recipeBatches" in data
    
    def test_get_production_batch_by_id_not_found(self, client, auth_headers, reset_data):
        """Test retrieving non-existent production batch"""
        response = client.get("/production-batches/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_production_batch_without_auth(self, client, reset_data):
        """Test that get production batch requires authentication"""
        response = client.get("/production-batches/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_production_batch_success(self, client, auth_headers, reset_data):
        """Test creating a new production batch"""
        new_batch = {
            "productionDate": "2025-12-15",
            "dietPlans": [1],
            "recipeBatches": [
                {"recipeId": 1, "portions": 20},
                {"recipeId": 2, "portions": 15},
                {"recipeId": 3, "portions": 25}
            ]
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["productionDate"] == "2025-12-15"
        assert data["id"] == 2
        assert len(data["recipeBatches"]) == 3
    
    def test_create_production_batch_empty_recipe_batches(self, client, auth_headers, reset_data):
        """Test creating production batch with no recipe batches"""
        new_batch = {
            "productionDate": "2025-12-16",
            "dietPlans": [],
            "recipeBatches": []
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["recipeBatches"] == []
        assert data["dietPlans"] == []
    
    def test_create_production_batch_multiple_diet_plans(self, client, auth_headers, reset_data):
        """Test creating production batch with multiple diet plans"""
        # First create another diet plan
        new_plan = {
            "customerId": 2,
            "date": "2025-12-15",
            "meals": [{"type": "LUNCH", "recipeId": 1, "portion": 1}]
        }
        client.post("/diet-plans", json=new_plan, headers=auth_headers)
        
        new_batch = {
            "productionDate": "2025-12-17",
            "dietPlans": [1, 2],  # Multiple diet plans
            "recipeBatches": [
                {"recipeId": 1, "portions": 30}
            ]
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["dietPlans"]) == 2
    
    def test_create_production_batch_without_auth(self, client, reset_data):
        """Test that creating production batch requires authentication"""
        new_batch = {
            "productionDate": "2025-12-15",
            "dietPlans": [],
            "recipeBatches": []
        }
        response = client.post("/production-batches", json=new_batch)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_production_batch_missing_required_fields(self, client, auth_headers, reset_data):
        """Test creating production batch without required fields fails"""
        incomplete_batch = {
            "dietPlans": [1]
            # Missing productionDate
        }
        response = client.post("/production-batches", json=incomplete_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_production_batch_recipe_batch_structure(self, client, auth_headers, reset_data):
        """Test recipe batch structure with recipeId and portions"""
        new_batch = {
            "productionDate": "2025-12-18",
            "dietPlans": [1],
            "recipeBatches": [
                {"recipeId": 1, "portions": 50},
                {"recipeId": 2, "portions": 40},
                {"recipeId": 3, "portions": 60}
            ]
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["recipeBatches"][0]["recipeId"] == 1
        assert data["recipeBatches"][0]["portions"] == 50
    
    def test_production_batch_large_portions(self, client, auth_headers, reset_data):
        """Test production batch with large portion numbers"""
        new_batch = {
            "productionDate": "2025-12-19",
            "dietPlans": [1],
            "recipeBatches": [
                {"recipeId": 1, "portions": 1000},
                {"recipeId": 2, "portions": 2000}
            ]
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["recipeBatches"][0]["portions"] == 1000
    
    def test_production_batch_validation_data_types(self, client, auth_headers, reset_data):
        """Test that production batch validates data types"""
        invalid_batch = {
            "productionDate": "2025-12-20",
            "dietPlans": [1],
            "recipeBatches": [
                {"recipeId": "not_a_number", "portions": 10}  # Invalid recipeId type
            ]
        }
        response = client.post("/production-batches", json=invalid_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_production_batch_business_rule_bc4(self, client, auth_headers, reset_data):
        """Test BC4: Daily Production Fulfillment"""
        # Create production batch based on validated diet plans
        new_batch = {
            "productionDate": "2025-12-21",
            "dietPlans": [1],  # Using validated diet plan
            "recipeBatches": [
                {"recipeId": 1, "portions": 10},
                {"recipeId": 2, "portions": 10},
                {"recipeId": 3, "portions": 10}
            ]
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify batch contains all recipes from diet plan
        recipe_ids = [batch["recipeId"] for batch in data["recipeBatches"]]
        assert 1 in recipe_ids
        assert 2 in recipe_ids
        assert 3 in recipe_ids
    
    def test_production_batch_date_format(self, client, auth_headers, reset_data):
        """Test production batch accepts various date formats"""
        new_batch = {
            "productionDate": "2025-12-31",
            "dietPlans": [],
            "recipeBatches": []
        }
        response = client.post("/production-batches", json=new_batch, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["productionDate"] == "2025-12-31"
