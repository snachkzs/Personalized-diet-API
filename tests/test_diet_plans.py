"""
Unit tests for diet plan endpoints
Coverage: CRUD operations, validation logic, business rules, edge cases
"""
import pytest
from fastapi import status


class TestDietPlans:
    """Test diet plan management endpoints"""
    
    def test_get_diet_plans_success(self, client, auth_headers, reset_data):
        """Test retrieving all diet plans"""
        response = client.get("/diet-plans", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
    
    def test_get_diet_plans_filter_by_customer(self, client, auth_headers, reset_data):
        """Test filtering diet plans by customer ID"""
        response = client.get("/diet-plans?customerId=1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(plan["customerId"] == 1 for plan in data)
    
    def test_get_diet_plans_filter_nonexistent_customer(self, client, auth_headers, reset_data):
        """Test filtering by non-existent customer returns empty list"""
        response = client.get("/diet-plans?customerId=999", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
    
    def test_get_diet_plans_without_auth(self, client, reset_data):
        """Test that diet plans endpoint requires authentication"""
        response = client.get("/diet-plans")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_diet_plan_by_id_success(self, client, auth_headers, reset_data):
        """Test retrieving a specific diet plan"""
        response = client.get("/diet-plans/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["customerId"] == 1
        assert len(data["meals"]) == 3
    
    def test_get_diet_plan_by_id_not_found(self, client, auth_headers, reset_data):
        """Test retrieving non-existent diet plan"""
        response = client.get("/diet-plans/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_diet_plan_without_auth(self, client, reset_data):
        """Test that get diet plan requires authentication"""
        response = client.get("/diet-plans/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_diet_plan_success(self, client, auth_headers, reset_data):
        """Test creating a new diet plan"""
        new_plan = {
            "customerId": 2,
            "date": "2025-12-15",
            "meals": [
                {"type": "BREAKFAST", "recipeId": 2, "portion": 1},
                {"type": "LUNCH", "recipeId": 3, "portion": 1},
                {"type": "DINNER", "recipeId": 1, "portion": 2}
            ]
        }
        response = client.post("/diet-plans", json=new_plan, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["customerId"] == 2
        assert data["id"] == 2
        assert len(data["meals"]) == 3
    
    def test_create_diet_plan_nonexistent_customer(self, client, auth_headers, reset_data):
        """Test creating diet plan for non-existent customer fails"""
        invalid_plan = {
            "customerId": 999,
            "date": "2025-12-15",
            "meals": []
        }
        response = client.post("/diet-plans", json=invalid_plan, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Customer not found" in response.json()["detail"]
    
    def test_create_diet_plan_without_meals(self, client, auth_headers, reset_data):
        """Test creating diet plan with no meals"""
        empty_plan = {
            "customerId": 1,
            "date": "2025-12-15",
            "meals": []
        }
        response = client.post("/diet-plans", json=empty_plan, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["meals"] == []
    
    def test_create_diet_plan_without_auth(self, client, reset_data):
        """Test that creating diet plan requires authentication"""
        new_plan = {
            "customerId": 1,
            "date": "2025-12-15",
            "meals": []
        }
        response = client.post("/diet-plans", json=new_plan)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_validate_diet_plan_success(self, client, auth_headers, reset_data):
        """Test validating a diet plan against customer goals"""
        response = client.post("/diet-plans/1/validate", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "valid" in data
        assert "total_nutrition" in data
        assert "goal" in data
        assert "differences" in data
    
    def test_validate_diet_plan_not_found(self, client, auth_headers, reset_data):
        """Test validating non-existent diet plan fails"""
        response = client.post("/diet-plans/999/validate", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_validate_diet_plan_without_auth(self, client, reset_data):
        """Test that validating diet plan requires authentication"""
        response = client.post("/diet-plans/1/validate")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_validate_diet_plan_calculates_nutrition(self, client, auth_headers, reset_data):
        """Test that validation correctly calculates total nutrition"""
        response = client.post("/diet-plans/1/validate", headers=auth_headers)
        data = response.json()
        
        # Plan has: Quinoa Bowl (420 cal) + Grilled Chicken (350 cal) + Salmon (450 cal)
        expected_calories = 420 + 350 + 450
        assert data["total_nutrition"]["calories"] == expected_calories
    
    def test_validate_diet_plan_with_portions(self, client, auth_headers, reset_data):
        """Test that validation accounts for portion sizes"""
        # Create plan with multiple portions
        new_plan = {
            "customerId": 1,
            "date": "2025-12-16",
            "meals": [
                {"type": "LUNCH", "recipeId": 1, "portion": 2}  # 2 portions
            ]
        }
        create_response = client.post("/diet-plans", json=new_plan, headers=auth_headers)
        plan_id = create_response.json()["id"]
        
        validate_response = client.post(f"/diet-plans/{plan_id}/validate", headers=auth_headers)
        data = validate_response.json()
        
        # Recipe 1 has 350 calories, with 2 portions = 700 calories
        assert data["total_nutrition"]["calories"] == 700
    
    def test_update_diet_plan_success(self, client, auth_headers, reset_data):
        """Test updating an existing diet plan"""
        updated_plan = {
            "customerId": 1,  # Must include customerId
            "date": "2025-12-20",
            "meals": [
                {"type": "BREAKFAST", "recipeId": 1, "portion": 1}
            ]
        }
        response = client.put("/diet-plans/1", json=updated_plan, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["date"] == "2025-12-20"
        assert len(data["meals"]) == 1
    
    def test_update_diet_plan_not_found(self, client, auth_headers, reset_data):
        """Test updating non-existent diet plan fails"""
        updated_plan = {
            "customerId": 1,
            "date": "2025-12-20",
            "meals": []
        }
        response = client.put("/diet-plans/999", json=updated_plan, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_diet_plan_without_auth(self, client, reset_data):
        """Test that updating diet plan requires authentication"""
        updated_plan = {
            "date": "2025-12-20",
            "meals": []
        }
        response = client.put("/diet-plans/1", json=updated_plan)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_diet_plan_success(self, client, auth_headers, reset_data):
        """Test deleting a diet plan"""
        response = client.delete("/diet-plans/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        get_response = client.get("/diet-plans/1", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_diet_plan_not_found(self, client, auth_headers, reset_data):
        """Test deleting non-existent diet plan fails"""
        response = client.delete("/diet-plans/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_diet_plan_without_auth(self, client, reset_data):
        """Test that deleting diet plan requires authentication"""
        response = client.delete("/diet-plans/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_diet_plan_meal_types(self, client, auth_headers, reset_data):
        """Test different meal types in diet plan"""
        plan_with_meal_types = {
            "customerId": 1,
            "date": "2025-12-18",
            "meals": [
                {"type": "BREAKFAST", "recipeId": 2, "portion": 1},
                {"type": "SNACK", "recipeId": 1, "portion": 1},
                {"type": "LUNCH", "recipeId": 3, "portion": 1},
                {"type": "SNACK", "recipeId": 2, "portion": 1},
                {"type": "DINNER", "recipeId": 1, "portion": 1}
            ]
        }
        response = client.post("/diet-plans", json=plan_with_meal_types, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["meals"]) == 5
    
    def test_diet_plan_validation_business_rule(self, client, auth_headers, reset_data):
        """Test BC1: Diet plan validation against nutritional goals"""
        # Customer 1 goal: 1900 calories, 100 protein, 230 carbs, 60 fat
        # Current plan total: 1220 calories (Quinoa 420 + Chicken 350 + Salmon 450)
        response = client.post("/diet-plans/1/validate", headers=auth_headers)
        data = response.json()
        
        assert "differences" in data
        assert data["goal"]["calories"] == 1900
        # Check if validation marks as invalid due to significant difference
        # (More than 10% difference)
        calorie_diff = abs(data["total_nutrition"]["calories"] - data["goal"]["calories"])
        if calorie_diff > data["goal"]["calories"] * 0.1:
            assert data["valid"] == False
