## New Feature: Power Operation

This final project extends Module 14 by adding a **Power** calculation operation.

### Power Operation
- **Description:** Calculates base raised to exponent (base^exponent)
- **Example:** 2^3 = 8
- **Usage:** Requires exactly 2 inputs: [base, exponent]
- **Implementation:** Uses Python's `**` operator

### Testing
- All 92 tests passing
- Comprehensive test coverage for power operation
- CI/CD pipeline validates every commit

# Final Project - IS601 Calculator API

A full-stack FastAPI calculator application with user authentication, JWT tokens, and comprehensive BREAD operations for calculations.

## 🎯 Project Overview

This project extends Module 14 by adding a **Power operation** to the calculator, along with complete testing coverage and CI/CD deployment.

### Features
- ✅ User registration and authentication (JWT tokens)
- ✅ Five calculation operations: Addition, Subtraction, Multiplication, Division, **Power**
- ✅ Full BREAD operations (Browse, Read, Edit, Add, Delete)
- ✅ RESTful API with FastAPI
- ✅ Comprehensive test suite (92 tests passing)
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Docker containerization and deployment

---

## 🚀 New Feature: Power Operation

### Description
The Power operation calculates base raised to exponent (base^exponent).

### Example
- Input: `[2, 3]`
- Result: `8` (2³ = 8)

### Usage
```json
POST /calculations
{
  "type": "power",
  "inputs": [2, 3]
}
```

### Implementation Details
- Requires exactly 2 inputs: `[base, exponent]`
- Uses Python's `**` operator
- Returns `ValueError` for invalid inputs
- Fully tested with unit, integration, and E2E tests

---

## 🐳 Docker Hub Repository

**Image:** [jav0613/final_project_is601](https://hub.docker.com/r/jav0613/final_project_is601)

**Pull the latest image:**
```bash
docker pull jav0613/final_project_is601:latest
```

---

## 💻 Running the Application

### Option 1: Using Docker (Recommended)

#### Pull and run from Docker Hub:
```bash
docker pull jav0613/final_project_is601:latest
docker run -p 8000:8000 jav0613/final_project_is601:latest
```

#### Or build and run locally:
```bash
docker build -t final_project_is601 .
docker run -p 8000:8000 final_project_is601
```

#### Using Docker Compose:
```bash
docker-compose up
```

**Access the application:**
- **Web UI:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

### Option 2: Running Locally (Without Docker)

#### Prerequisites:
- Python 3.10+
- pip
- Virtual environment (recommended)

#### Steps:

1. **Clone the repository:**
```bash
git clone https://github.com/jorgeavergara522/final_project_is601.git
cd final_project_is601
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install --with-deps chromium  # For E2E tests
```

4. **Run the application:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Access the application:**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🧪 Running Tests Locally

### Run All Tests:
```bash
TESTING=true pytest -v
```

### Run Specific Test Suites:

**Unit Tests:**
```bash
TESTING=true pytest tests/unit/ -v
```

**Integration Tests:**
```bash
TESTING=true pytest tests/integration/ -v
```

**E2E Tests:**
```bash
E2E_TESTS=true pytest tests/e2e/ -v
```

### Run Tests with Coverage:
```bash
TESTING=true pytest --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

### Test Summary:
- **Total Tests:** 92 passing, 2 skipped
- **Unit Tests:** All passing
- **Integration Tests:** All passing
- **E2E Tests:** All passing
- **Coverage:** 95%+

---

## 📁 Project Structure
```
final_project_is601/
├── app/
│   ├── auth/
│   │   ├── dependencies.py    # Auth dependencies
│   │   ├── hashing.py         # Password hashing
│   │   └── jwt.py             # JWT token management
│   ├── models/
│   │   ├── calculation.py     # Calculation model (includes Power)
│   │   └── user.py            # User model
│   ├── operations/
│   │   └── __init__.py        # Calculator operations
│   ├── schemas/
│   │   ├── calculation.py     # Calculation schemas
│   │   ├── token.py           # Token schemas
│   │   └── user.py            # User schemas
│   ├── database.py            # Database configuration
│   └── main.py                # FastAPI application
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── templates/                 # HTML templates
├── static/                    # Static files (CSS, JS)
├── .github/workflows/         # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/fastapi_db

# JWT Settings
JWT_SECRET_KEY=your-secret-key-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Testing
TESTING=false
```

---

## 🚦 CI/CD Pipeline

### GitHub Actions Workflow

The project includes a complete CI/CD pipeline that:

1. ✅ **Runs all tests** (unit, integration, E2E)
2. ✅ **Scans for security vulnerabilities** (Trivy)
3. ✅ **Builds Docker image**
4. ✅ **Deploys to Docker Hub** (on main branch)

**View the latest build:**
https://github.com/jorgeavergara522/final_project_is601/actions

---

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (JSON)
- `POST /auth/token` - Login (OAuth2 form)

### Calculations
- `POST /calculations` - Create calculation
- `GET /calculations` - List user's calculations
- `GET /calculations/{id}` - Get specific calculation
- `PUT /calculations/{id}` - Update calculation
- `DELETE /calculations/{id}` - Delete calculation

### Health
- `GET /health` - Health check

---

## 🧮 Calculation Types

| Operation        | Type             | Example              | Result |
|-----------------|------------------|----------------------|--------|
| Addition        | `addition`       | `[1, 2, 3]`          | `6`    |
| Subtraction     | `subtraction`    | `[10, 3, 2]`         | `5`    |
| Multiplication  | `multiplication` | `[2, 3, 4]`          | `24`   |
| Division        | `division`       | `[100, 2, 5]`        | `10`   |
| **Power** ✨    | `power`          | `[2, 3]`             | `8`    |

---

## 👨‍💻 Author

**Jorge Avergara**
- GitHub: [@jorgeavergara522](https://github.com/jorgeavergara522)
- Docker Hub: [jav0613](https://hub.docker.com/u/jav0613)
- Course: IS601 - Python for Web API Development (Fall 2025)

---

## 📝 Reflection

### What I Learned

This final project reinforced key concepts in full-stack web development:

1. **FastAPI Framework:** Building RESTful APIs with automatic documentation
2. **SQLAlchemy ORM:** Database modeling with polymorphic inheritance
3. **JWT Authentication:** Secure token-based authentication with refresh tokens
4. **Testing:** Writing comprehensive unit, integration, and E2E tests
5. **Docker:** Containerization and multi-platform deployment
6. **CI/CD:** Automating testing, security scanning, and deployment with GitHub Actions

### Challenges Overcome

- **Circular Import Issues:** Resolved by restructuring JWT authentication module
- **Test Isolation:** Fixed Faker unique conflicts by using UUID-based generation
- **Database Management:** Properly handling SQLite for tests vs PostgreSQL for production
- **E2E Testing:** Configuring lifespan to reset database only for E2E runs

### Power Operation Implementation

Adding the Power operation required:
- Creating `Power` subclass in `calculation.py`
- Adding `POWER` enum to calculation schemas
- Implementing `power()` function in operations
- Writing comprehensive tests at all levels
- Updating UI templates and API documentation

The polymorphic factory pattern made this straightforward and maintainable.

---

## 📄 License

This project is for educational purposes as part of the IS601 course at NJIT.

---

## 🙏 Acknowledgments

- Professor Keith Williams for course guidance
- NJIT IS601 Fall 2025 course materials
- FastAPI and SQLAlchemy documentation




# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Verify Homebrew:**

```bash
brew --version
```

If you see a version number, you're good to go.

---

# 🧩 2. Install and Configure Git

## Install Git

- **MacOS (using Homebrew)**

```bash
brew install git
```

- **Windows**

Download and install [Git for Windows](https://git-scm.com/download/win).  
Accept the default options during installation.

**Verify Git:**

```bash
git --version
```

---

## Configure Git Globals

Set your name and email so Git tracks your commits properly:

```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

Confirm the settings:

```bash
git config --list
```

---

## Generate SSH Keys and Connect to GitHub

> Only do this once per machine.

1. Generate a new SSH key:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

(Press Enter at all prompts.)

2. Start the SSH agent:

```bash
eval "$(ssh-agent -s)"
```

3. Add the SSH private key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

4. Copy your SSH public key:

- **Mac/Linux:**

```bash
cat ~/.ssh/id_ed25519.pub | pbcopy
```

- **Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

5. Add the key to your GitHub account:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click **New SSH Key**, paste the key, save.

6. Test the connection:

```bash
ssh -T git@github.com
```

You should see a success message.

---

# 🧩 3. Clone the Repository

Now you can safely clone the course project:

```bash
git clone <repository-url>
cd <repository-directory>
```

---

# 🛠️ 4. Install Python 3.10+

## Install Python

- **MacOS (Homebrew)**

```bash
brew install python
```

- **Windows**

Download and install [Python for Windows](https://www.python.org/downloads/).  
✅ Make sure you **check the box** `Add Python to PATH` during setup.

**Verify Python:**

```bash
python3 --version
```
or
```bash
python --version
```

---

## Create and Activate a Virtual Environment

(Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🐳 5. (Optional) Docker Setup

> Skip if Docker isn't used in this module.

## Install Docker

- [Install Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

## Build Docker Image

```bash
docker build -t <image-name> .
```

## Run Docker Container

```bash
docker run -it --rm <image-name>
```

---

# 🚀 6. Running the Project

- **Without Docker**:

```bash
python main.py
```

(or update this if the main script is different.)

- **With Docker**:

```bash
docker run -it --rm <image-name>
```

---

# 📝 7. Submission Instructions

After finishing your work:

```bash
git add .
git commit -m "Complete Module X"
git push origin main
```

Then submit the GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action                         | Command                                          |
| ------------------------------- | ------------------------------------------------ |
| Install Homebrew (Mac)          | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Install Git                     | `brew install git` or Git for Windows installer |
| Configure Git Global Username  | `git config --global user.name "Your Name"`      |
| Configure Git Global Email     | `git config --global user.email "you@example.com"` |
| Clone Repository                | `git clone <repo-url>`                          |
| Create Virtual Environment     | `python3 -m venv venv`                           |
| Activate Virtual Environment   | `source venv/bin/activate` / `venv\Scripts\activate.bat` |
| Install Python Packages        | `pip install -r requirements.txt`               |
| Build Docker Image              | `docker build -t <image-name> .`                |
| Run Docker Container            | `docker run -it --rm <image-name>`               |
| Push Code to GitHub             | `git add . && git commit -m "message" && git push` |

---

# 📋 Notes

- Install **Homebrew** first on Mac.
- Install and configure **Git** and **SSH** before cloning.
- Use **Python 3.10+** and **virtual environments** for Python projects.
- **Docker** is optional depending on the project.

---

# 📎 Quick Links

- [Homebrew](https://brew.sh/)
- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
# Module 14 Assignment
