"""
Unit tests for recipe endpoints
Coverage: CRUD operations, authentication, validation, edge cases
"""
import pytest
from fastapi import status


class TestRecipes:
    """Test recipe management endpoints"""
    
    def test_get_recipes_success(self, client, auth_headers, reset_data):
        """Test retrieving all recipes with authentication"""
        response = client.get("/recipes", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Grilled Chicken Salad"
    
    def test_get_recipes_without_auth(self, client, reset_data):
        """Test that recipes endpoint requires authentication"""
        response = client.get("/recipes")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_recipe_by_id_success(self, client, auth_headers, reset_data):
        """Test retrieving a specific recipe"""
        response = client.get("/recipes/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Grilled Chicken Salad"
        assert "ingredients" in data
        assert "nutrition" in data
    
    def test_get_recipe_by_id_not_found(self, client, auth_headers, reset_data):
        """Test retrieving non-existent recipe"""
        response = client.get("/recipes/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_recipe_without_auth(self, client, reset_data):
        """Test that get recipe by ID requires authentication"""
        response = client.get("/recipes/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_recipe_success(self, client, auth_headers, reset_data):
        """Test adding a new recipe"""
        new_recipe = {
            "name": "Veggie Pasta",
            "ingredients": ["pasta", "tomatoes", "garlic", "olive oil", "basil"],
            "nutrition": {
                "calories": 380,
                "protein": 12,
                "carbs": 70,
                "fat": 8
            }
        }
        response = client.post("/recipes", json=new_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Veggie Pasta"
        assert data["id"] == 4
        assert len(data["ingredients"]) == 5
    
    def test_add_recipe_without_ingredients(self, client, auth_headers, reset_data):
        """Test adding recipe with empty ingredients list"""
        new_recipe = {
            "name": "Simple Recipe",
            "nutrition": {
                "calories": 200,
                "protein": 10,
                "carbs": 30,
                "fat": 5
            }
        }
        response = client.post("/recipes", json=new_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["ingredients"] == []
    
    def test_add_recipe_missing_required_fields(self, client, auth_headers, reset_data):
        """Test adding recipe without required fields fails"""
        incomplete_recipe = {
            "name": "Incomplete Recipe"
        }
        response = client.post("/recipes", json=incomplete_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_add_recipe_without_auth(self, client, reset_data):
        """Test that adding recipe requires authentication"""
        new_recipe = {
            "name": "Test Recipe",
            "nutrition": {"calories": 300, "protein": 15, "carbs": 40, "fat": 10}
        }
        response = client.post("/recipes", json=new_recipe)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_recipe_success(self, client, auth_headers, reset_data):
        """Test updating an existing recipe"""
        updated_recipe = {
            "name": "Updated Chicken Salad",
            "ingredients": ["chicken", "mixed greens", "cherry tomatoes", "balsamic vinegar"],
            "nutrition": {
                "calories": 360,
                "protein": 42,
                "carbs": 18,
                "fat": 16
            }
        }
        response = client.put("/recipes/1", json=updated_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Chicken Salad"
        assert data["nutrition"]["calories"] == 360
    
    def test_update_recipe_not_found(self, client, auth_headers, reset_data):
        """Test updating non-existent recipe fails"""
        updated_recipe = {
            "name": "Ghost Recipe",
            "nutrition": {"calories": 100, "protein": 5, "carbs": 15, "fat": 3}
        }
        response = client.put("/recipes/999", json=updated_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_recipe_without_auth(self, client, reset_data):
        """Test that updating recipe requires authentication"""
        updated_recipe = {
            "name": "Test",
            "nutrition": {"calories": 300, "protein": 15, "carbs": 40, "fat": 10}
        }
        response = client.put("/recipes/1", json=updated_recipe)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_recipe_success(self, client, auth_headers, reset_data):
        """Test deleting a recipe"""
        response = client.delete("/recipes/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]
        
        # Verify deletion
        get_response = client.get("/recipes/1", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_recipe_not_found(self, client, auth_headers, reset_data):
        """Test deleting non-existent recipe fails"""
        response = client.delete("/recipes/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_recipe_without_auth(self, client, reset_data):
        """Test that deleting recipe requires authentication"""
        response = client.delete("/recipes/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_recipe_nutrition_validation(self, client, auth_headers, reset_data):
        """Test that nutrition values are validated"""
        invalid_recipe = {
            "name": "Invalid Recipe",
            "nutrition": {
                "calories": "not_a_number",  # Should be int
                "protein": 15,
                "carbs": 40,
                "fat": 10
            }
        }
        response = client.post("/recipes", json=invalid_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recipe_complete_nutrition_facts(self, client, auth_headers, reset_data):
        """Test that all nutrition facts are required"""
        incomplete_nutrition = {
            "name": "Incomplete Nutrition",
            "nutrition": {
                "calories": 300,
                "protein": 15
                # Missing carbs and fat
            }
        }
        response = client.post("/recipes", json=incomplete_nutrition, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_recipe_with_multiple_ingredients(self, client, auth_headers, reset_data):
        """Test recipe with complex ingredient list"""
        complex_recipe = {
            "name": "Complex Dish",
            "ingredients": [
                "ingredient1", "ingredient2", "ingredient3", 
                "ingredient4", "ingredient5", "ingredient6",
                "ingredient7", "ingredient8", "ingredient9", "ingredient10"
            ],
            "nutrition": {"calories": 500, "protein": 25, "carbs": 60, "fat": 20}
        }
        response = client.post("/recipes", json=complex_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["ingredients"]) == 10
    
    def test_recipe_nutrition_zero_values(self, client, auth_headers, reset_data):
        """Test recipe with zero nutrition values (edge case)"""
        zero_nutrition_recipe = {
            "name": "Zero Calorie Item",
            "nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        }
        response = client.post("/recipes", json=zero_nutrition_recipe, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nutrition"]["calories"] == 0
