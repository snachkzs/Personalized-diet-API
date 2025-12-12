# Personalized Diet Planning API

![CI/CD Pipeline](https://github.com/snachkzs/Personalized-diet-API/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![License](https://img.shields.io/badge/license-MIT-green)

API untuk manajemen diet plan yang dipersonalisasi dengan autentikasi JWT, validasi nutrisi, dan production batch management.

## Features

- **JWT Authentication** - Sistem autentikasi dengan JWT tokens untuk melindungi semua endpoint
- **Customer Management** - CRUD operations untuk data customer dengan dietary restrictions dan nutritional goals
- **Recipe Management** - Manajemen resep dengan informasi nutrisi lengkap
- **Diet Plan Management** - Pembuatan dan validasi diet plan berdasarkan kebutuhan customer
- **Diet Plan Validation (BC1)** - Validasi otomatis diet plan terhadap nutritional goals customer
- **Production Batch Management (BC4)** - Daily production fulfillment dari validated diet plans
- **95%+ Test Coverage** - Comprehensive unit tests dengan TDD approach
- **CI/CD Pipeline** - Automated testing dan deployment dengan GitHub Actions

## Requirements

- Python 3.11+
- pip

## Quick Start

### Local Development

1. **Clone repository**
```bash
git clone https://github.com/snachkzs/Personalized-diet-API.git
cd Personalized-diet-API
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# atau
.venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

API akan berjalan di `http://localhost:8001`

## API Documentation

Setelah menjalankan aplikasi, akses dokumentasi interaktif di:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Authentication

API menggunakan JWT (JSON Web Token) untuk autentikasi. Semua endpoint (kecuali `/register` dan `/login`) memerlukan token.

### Default Credentials
```
Username: admin
Password: secret
```

### Authentication Flow

1. **Register** (optional - untuk user baru)
```bash
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "email": "user@example.com",
    "full_name": "New User"
  }'
```

2. **Login** untuk mendapatkan token
```bash
curl -X POST "http://localhost:8001/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. **Gunakan token** untuk mengakses protected endpoints
```bash
curl -X GET "http://localhost:8001/customers" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register user baru | No |
| POST | `/login` | Login dan dapatkan token | No |
| GET | `/users/me` | Get current user info | Yes |

### Customer Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/customers` | Get all customers | Yes |
| GET | `/customers/{id}` | Get customer by ID | Yes |
| POST | `/customers` | Create new customer | Yes |
| PUT | `/customers/{id}` | Update customer | Yes |
| DELETE | `/customers/{id}` | Delete customer | Yes |

### Recipe Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/recipes` | Get all recipes | Yes |
| GET | `/recipes/{id}` | Get recipe by ID | Yes |
| POST | `/recipes` | Create new recipe | Yes |
| PUT | `/recipes/{id}` | Update recipe | Yes |
| DELETE | `/recipes/{id}` | Delete recipe | Yes |

### Diet Plan Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/diet-plans` | Get all diet plans | Yes |
| GET | `/diet-plans?customerId={id}` | Filter by customer | Yes |
| GET | `/diet-plans/{id}` | Get diet plan by ID | Yes |
| POST | `/diet-plans` | Create new diet plan | Yes |
| POST | `/diet-plans/{id}/validate` | Validate diet plan (BC1) | Yes |
| PUT | `/diet-plans/{id}` | Update diet plan | Yes |
| DELETE | `/diet-plans/{id}` | Delete diet plan | Yes |

### Production Batch Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/production-batches` | Get all batches | Yes |
| GET | `/production-batches/{id}` | Get batch by ID | Yes |
| POST | `/production-batches` | Create batch (BC4) | Yes |

## Example Usage

### 1. Create a Customer
```bash
curl -X POST "http://localhost:8001/customers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "restrictions": [
      {
        "type": "Vegetarian",
        "description": "No meat products"
      }
    ],
    "goal": {
      "calories": 2000,
      "protein": 100,
      "carbs": 250,
      "fat": 65
    }
  }'
```

### 2. Create a Recipe
```bash
curl -X POST "http://localhost:8001/recipes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Healthy Salad",
    "ingredients": ["lettuce", "tomatoes", "cucumber", "olive oil"],
    "nutrition": {
      "calories": 150,
      "protein": 5,
      "carbs": 20,
      "fat": 8
    }
  }'
```

### 3. Create a Diet Plan
```bash
curl -X POST "http://localhost:8001/diet-plans" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": 1,
    "date": "2025-12-15",
    "meals": [
      {
        "type": "BREAKFAST",
        "recipeId": 2,
        "portion": 1
      },
      {
        "type": "LUNCH",
        "recipeId": 1,
        "portion": 1
      },
      {
        "type": "DINNER",
        "recipeId": 3,
        "portion": 1
      }
    ]
  }'
```

### 4. Validate Diet Plan (BC1)
```bash
curl -X POST "http://localhost:8001/diet-plans/1/validate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "valid": true,
  "total_nutrition": {
    "calories": 1950,
    "protein": 98,
    "carbs": 245,
    "fat": 62
  },
  "goal": {
    "calories": 2000,
    "protein": 100,
    "carbs": 250,
    "fat": 65
  },
  "differences": {
    "calories": 50,
    "protein": 2,
    "carbs": 5,
    "fat": 3
  },
  "restrictions_met": true
}
```

### 5. Create Production Batch (BC4)
```bash
curl -X POST "http://localhost:8001/production-batches" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "productionDate": "2025-12-15",
    "dietPlans": [1, 2, 3],
    "recipeBatches": [
      {
        "recipeId": 1,
        "portions": 50
      },
      {
        "recipeId": 2,
        "portions": 40
      },
      {
        "recipeId": 3,
        "portions": 60
      }
    ]
  }'
```

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Coverage
Project ini mengimplementasikan TDD dengan minimal 95% test coverage, mencakup:
- Authentication flows
- CRUD operations
- Business logic (BC1, BC4)
- Edge cases
- Error handling
- Security validation

View coverage report setelah running tests di `htmlcov/index.html`

## Project Structure

```
Personalized-diet-API/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD pipeline
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_auth.py            # Authentication tests
│   ├── test_customers.py       # Customer endpoint tests
│   ├── test_recipes.py         # Recipe endpoint tests
│   ├── test_diet_plans.py      # Diet plan endpoint tests
│   └── test_production_batches.py  # Production batch tests
├── main.py                     # Main application file
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .coveragerc                 # Coverage configuration
└── README.md                   # This file
```

## Configuration

### Environment Variables

Buat file `.env` untuk konfigurasi (optional):
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Security Configuration

**PENTING untuk Production:**
1. Ganti `SECRET_KEY` di `main.py` dengan key yang secure
2. Generate secret key dengan:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
3. Gunakan HTTPS untuk production deployment
4. Set environment variables dengan nilai yang secure

## Deployment

### Deploy ke Railway

1. Fork repository ini
2. Sign up di [Railway](https://railway.app)
3. Create new project → Deploy from GitHub
4. Pilih repository Anda
5. Set environment variables di Railway dashboard
6. Deploy!

### Deploy ke Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` di project directory
3. Follow the prompts
4. Set environment variables di Vercel dashboard

### Deploy ke Heroku

```bash
# Login ke Heroku
heroku login

# Create app
heroku create your-app-name

# Set config
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main
```

## Business Rules

### BC1: Diet Plan Validation
- Validasi diet plan terhadap customer's nutritional goals
- Menghitung total nutrition dari semua meals
- Membandingkan dengan target customer
- Mengidentifikasi perbedaan > 10% sebagai invalid
- Mempertimbangkan portion sizes

### BC4: Daily Production Fulfillment
- Create production batches dari validated diet plans
- Aggregate recipe requirements
- Calculate total portions needed
- Support multiple diet plans per batch

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Authors

- **snachkzs** - [GitHub Profile](https://github.com/snachkzs)

## Acknowledgments

- FastAPI framework
- JWT for authentication
- pytest for testing

## Support

Jika ada pertanyaan atau issues, silakan:
- Open an issue di GitHub
- Contact: [GitHub Issues](https://github.com/snachkzs/Personalized-diet-API/issues)

---

**Made with FastAPI and Test-Driven Development**
