"""
Test fixtures and configuration for pytest
"""
import pytest
from fastapi.testclient import TestClient
from main import app, users_db, customers, recipes, diet_plans, production_batches


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def reset_data():
    """Reset all data stores to initial state after each test"""
    # Store original references
    import main
    original_customers = list(main.customers)
    original_recipes = list(main.recipes)
    original_diet_plans = list(main.diet_plans)
    original_production_batches = list(main.production_batches)
    original_users = dict(main.users_db)
    
    yield
    
    # Reset to original state
    main.customers.clear()
    main.customers.extend(original_customers)
    
    main.recipes.clear()
    main.recipes.extend(original_recipes)
    
    main.diet_plans.clear()
    main.diet_plans.extend(original_diet_plans)
    
    main.production_batches.clear()
    main.production_batches.extend(original_production_batches)
    
    main.users_db.clear()
    main.users_db.update(original_users)
    
    # Reset counters
    main.next_customer_id = 4
    main.next_recipe_id = 4
    main.next_diet_plan_id = 2
    main.next_production_batch_id = 2


@pytest.fixture(scope="function")
def auth_token(client, reset_data):
    """Get authentication token for testing protected endpoints"""
    response = client.post(
        "/login",
        data={"username": "admin", "password": "secret"}
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}
