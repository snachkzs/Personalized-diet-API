from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this to a secure random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Personalized Diet Planning API")

# ===================== AUTH MODELS =====================

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

# ===================== DATA MODELS =====================

class NutritionalGoal(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class DietaryRestriction(BaseModel):
    type: str
    description: str

class Customer(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = ""
    restrictions: List[DietaryRestriction] = []
    goal: NutritionalGoal

class NutritionalFacts(BaseModel):
    calories: int
    protein: int
    carbs: int
    fat: int

class Recipe(BaseModel):
    id: Optional[int] = None
    name: str
    ingredients: List[str] = []
    nutrition: NutritionalFacts

class MealPlan(BaseModel):
    type: str
    recipeId: int
    portion: int = 1

class DietPlan(BaseModel):
    id: Optional[int] = None
    customerId: int
    date: str
    meals: List[MealPlan] = []

class RecipeBatch(BaseModel):
    recipeId: int
    portions: int

class ProductionBatch(BaseModel):
    id: Optional[int] = None
    productionDate: str
    dietPlans: List[int] = []
    recipeBatches: List[RecipeBatch] = []

# ===================== AUTH UTILITIES =====================

# In-memory user database (for demo purposes)
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ===================== DATA STORAGE =====================

customers = [
    {
        'id': 1, 
        'name': 'Alma', 
        'email': 'Alma@example.com', 
        'phone': '123-456-7890', 
        'restrictions': [
            {'type': 'Vegetarian', 'description': 'No meat products'},
            {'type': 'Allergy', 'description': 'Cashew allergy'}
        ], 
        'goal': {'calories': 1800, 'protein': 80, 'carbs': 200, 'fat': 60}
    },
    {
        'id': 2, 
        'name': 'Felicia', 
        'email': 'Felicia@example.com', 
        'phone': '123-333-333', 
        'restrictions': [], 
        'goal': {'calories': 2000, 'protein': 120, 'carbs': 250, 'fat': 65}
    },
    {
        'id': 3, 
        'name': 'Vielrizki', 
        'email': 'Vielrizki@example.com', 
        'phone': '123-444-4444', 
        'restrictions': [
            {'type': 'Gluten-free', 'description': 'No gluten products'}
        ], 
        'goal': {'calories': 2500, 'protein': 150, 'carbs': 280, 'fat': 80}
    }
]

recipes = [
    {
        'id': 1,
        'name': 'Grilled Chicken Salad',
        'ingredients': ['chicken breast', 'lettuce', 'tomato', 'olive oil'],
        'nutrition': {'calories': 350, 'protein': 40, 'carbs': 15, 'fat': 18}
    },
    {
        'id': 2,
        'name': 'Quinoa Bowl',
        'ingredients': ['quinoa', 'chickpeas', 'vegetables', 'tahini'],
        'nutrition': {'calories': 420, 'protein': 18, 'carbs': 65, 'fat': 12}
    },
    {
        'id': 3,
        'name': 'Salmon with Vegetables',
        'ingredients': ['salmon fillet', 'broccoli', 'carrots', 'lemon'],
        'nutrition': {'calories': 450, 'protein': 38, 'carbs': 20, 'fat': 25}
    }
]

diet_plans = [
    {
        'id': 1,
        'customerId': 1,
        'date': '2025-11-17',
        'meals': [
            {'type': 'BREAKFAST', 'recipeId': 2, 'portion': 1},
            {'type': 'LUNCH', 'recipeId': 1, 'portion': 1},
            {'type': 'DINNER', 'recipeId': 3, 'portion': 1}
        ]
    }
]

production_batches = [
    {
        'id': 1,
        'productionDate': '2025-11-17',
        'dietPlans': [1],
        'recipeBatches': [
            {'recipeId': 1, 'portions': 10},
            {'recipeId': 2, 'portions': 10},
            {'recipeId': 3, 'portions': 10}
        ]
    }
]

next_customer_id = 4
next_recipe_id = 4
next_diet_plan_id = 2
next_production_batch_id = 2

# ===================== AUTH ENDPOINTS =====================

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """Register a new user"""
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    users_db[user.username] = user_dict
    return User(**user_dict)

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current logged in user info"""
    return current_user

# ===================== CUSTOMER ENDPOINTS =====================

@app.get('/customers')
def get_customers(current_user: User = Depends(get_current_active_user)):
    return customers

@app.get('/customers/{customer_id}')
def get_customer_by_id(customer_id: int, current_user: User = Depends(get_current_active_user)):
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if customer:
        return customer
    raise HTTPException(status_code=404, detail='Customer not found')

@app.post('/customers', status_code=201)
def add_customer(customer: Customer, current_user: User = Depends(get_current_active_user)):
    global next_customer_id
    
    new_customer = {
        'id': next_customer_id,
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'restrictions': [r.model_dump() for r in customer.restrictions],
        'goal': customer.goal.model_dump()
    }
    customers.append(new_customer)
    next_customer_id += 1
    return new_customer

@app.put('/customers/{customer_id}')
def update_customer(customer_id: int, customer: Customer, current_user: User = Depends(get_current_active_user)):
    existing_customer = next((c for c in customers if c['id'] == customer_id), None)
    if not existing_customer:
        raise HTTPException(status_code=404, detail='Customer not found')
    
    existing_customer.update({
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'restrictions': [r.model_dump() for r in customer.restrictions],
        'goal': customer.goal.model_dump()
    })
    return existing_customer

@app.delete('/customers/{customer_id}')
def delete_customer(customer_id: int, current_user: User = Depends(get_current_active_user)):
    global customers
    customer = next((c for c in customers if c['id'] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found')
    
    customers = [c for c in customers if c['id'] != customer_id]
    return {'message': 'Customer deleted successfully'}

# ===================== RECIPE ENDPOINTS =====================

@app.get('/recipes')
def get_recipes(current_user: User = Depends(get_current_active_user)):
    return recipes

@app.get('/recipes/{recipe_id}')
def get_recipe_by_id(recipe_id: int, current_user: User = Depends(get_current_active_user)):
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if recipe:
        return recipe
    raise HTTPException(status_code=404, detail='Recipe not found')

@app.post('/recipes', status_code=201)
def add_recipe(recipe: Recipe, current_user: User = Depends(get_current_active_user)):
    global next_recipe_id
    
    new_recipe = {
        'id': next_recipe_id,
        'name': recipe.name,
        'ingredients': recipe.ingredients,
        'nutrition': recipe.nutrition.model_dump()
    }
    recipes.append(new_recipe)
    next_recipe_id += 1
    return new_recipe

@app.put('/recipes/{recipe_id}')
def update_recipe(recipe_id: int, recipe: Recipe, current_user: User = Depends(get_current_active_user)):
    existing_recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if not existing_recipe:
        raise HTTPException(status_code=404, detail='Recipe not found')
    
    existing_recipe.update({
        'name': recipe.name,
        'ingredients': recipe.ingredients,
        'nutrition': recipe.nutrition.model_dump()
    })
    return existing_recipe

@app.delete('/recipes/{recipe_id}')
def delete_recipe(recipe_id: int, current_user: User = Depends(get_current_active_user)):
    global recipes
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if not recipe:
        raise HTTPException(status_code=404, detail='Recipe not found')
    
    recipes = [r for r in recipes if r['id'] != recipe_id]
    return {'message': 'Recipe deleted successfully'}

# ===================== DIET PLAN ENDPOINTS =====================

@app.get('/diet-plans')
def get_diet_plans(customerId: Optional[int] = Query(None), current_user: User = Depends(get_current_active_user)):
    if customerId:
        filtered = [dp for dp in diet_plans if dp['customerId'] == customerId]
        return filtered
    return diet_plans

@app.get('/diet-plans/{plan_id}')
def get_diet_plan_by_id(plan_id: int, current_user: User = Depends(get_current_active_user)):
    plan = next((dp for dp in diet_plans if dp['id'] == plan_id), None)
    if plan:
        return plan
    raise HTTPException(status_code=404, detail='Diet plan not found')

@app.post('/diet-plans', status_code=201)
def create_diet_plan(diet_plan: DietPlan, current_user: User = Depends(get_current_active_user)):
    global next_diet_plan_id
    
    customer = next((c for c in customers if c['id'] == diet_plan.customerId), None)
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found')
    
    new_plan = {
        'id': next_diet_plan_id,
        'customerId': diet_plan.customerId,
        'date': diet_plan.date,
        'meals': [m.model_dump() for m in diet_plan.meals]
    }
    diet_plans.append(new_plan)
    next_diet_plan_id += 1
    return new_plan

@app.post('/diet-plans/{plan_id}/validate')
def validate_diet_plan(plan_id: int, current_user: User = Depends(get_current_active_user)):
    """BC1: Validate DietPlan against Customer's NutritionalGoal and DietaryRestriction"""
    plan = next((dp for dp in diet_plans if dp['id'] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail='Diet plan not found')
    
    customer = next((c for c in customers if c['id'] == plan['customerId']), None)
    if not customer:
        raise HTTPException(status_code=404, detail='Customer not found')
    
    total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    for meal in plan['meals']:
        recipe = next((r for r in recipes if r['id'] == meal['recipeId']), None)
        if recipe:
            portion = meal.get('portion', 1)
            for key in total_nutrition:
                total_nutrition[key] += recipe['nutrition'][key] * portion
    
    goal = customer['goal']
    validation_result = {
        'valid': True,
        'total_nutrition': total_nutrition,
        'goal': goal,
        'differences': {},
        'restrictions_met': True
    }
    
    for key in total_nutrition:
        diff = abs(total_nutrition[key] - goal[key])
        validation_result['differences'][key] = diff
        if diff > goal[key] * 0.1:
            validation_result['valid'] = False
    
    return validation_result

@app.put('/diet-plans/{plan_id}')
def update_diet_plan(plan_id: int, diet_plan: DietPlan, current_user: User = Depends(get_current_active_user)):
    plan = next((dp for dp in diet_plans if dp['id'] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail='Diet plan not found')
    
    plan.update({
        'date': diet_plan.date,
        'meals': [m.model_dump() for m in diet_plan.meals]
    })
    return plan

@app.delete('/diet-plans/{plan_id}')
def delete_diet_plan(plan_id: int, current_user: User = Depends(get_current_active_user)):
    global diet_plans
    plan = next((dp for dp in diet_plans if dp['id'] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail='Diet plan not found')
    
    diet_plans = [dp for dp in diet_plans if dp['id'] != plan_id]
    return {'message': 'Diet plan deleted successfully'}

# ===================== PRODUCTION BATCH ENDPOINTS =====================

@app.get('/production-batches')
def get_production_batches(current_user: User = Depends(get_current_active_user)):
    return production_batches

@app.get('/production-batches/{batch_id}')
def get_production_batch_by_id(batch_id: int, current_user: User = Depends(get_current_active_user)):
    batch = next((pb for pb in production_batches if pb['id'] == batch_id), None)
    if batch:
        return batch
    raise HTTPException(status_code=404, detail='Production batch not found')

@app.post('/production-batches', status_code=201)
def create_production_batch(batch: ProductionBatch, current_user: User = Depends(get_current_active_user)):
    """BC4: Daily Production Fulfillment - Create production batch from validated diet plans"""
    global next_production_batch_id
    
    new_batch = {
        'id': next_production_batch_id,
        'productionDate': batch.productionDate,
        'dietPlans': batch.dietPlans,
        'recipeBatches': [rb.model_dump() for rb in batch.recipeBatches]
    }
    production_batches.append(new_batch)
    next_production_batch_id += 1
    return new_batch

# ===================== MAIN =====================

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)