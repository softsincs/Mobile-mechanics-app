# 🚀 CI/CD Setup Guide

This document explains the GitHub Actions CI/CD pipeline for MobileMechanic.

## 📋 Overview

The project uses GitHub Actions for:
- **CI (Continuous Integration)**: Run tests, linting, security checks on every push/PR
- **CD (Continuous Deployment)**: Auto-deploy to production after successful CI
- **Scheduled Checks**: Daily/weekly health checks and dependency audits

## 📁 Workflow Files

### 1. `.github/workflows/ci.yml` - Continuous Integration
Runs on every push to `main` or `develop` branches and pull requests.

**Jobs:**
- **test**: Runs pytest, generates coverage reports
  - Tests on Python 3.11 & 3.12
  - Runs migrations
  - Django system checks
  - Coverage upload to Codecov
  
- **lint**: Code quality checks
  - flake8 for style
  - black for formatting
  - isort for imports
  
- **security**: Security scanning
  - Bandit for code vulnerabilities
  - Safety for dependency vulnerabilities

**Artifacts:**
- HTML coverage reports
- Security scan results
- Test results

### 2. `.github/workflows/cd.yml` - Continuous Deployment
Triggers after successful CI or on direct push to `main`.

**Jobs:**
- **deploy**: Deployment process
  - Builds Docker image
  - Pushes to Docker Hub
  - Runs migrations
  - Collects static files

**Supports:**
- Heroku (uncomment lines)
- AWS Elastic Beanstalk (uncomment lines)
- Railway (uncomment lines)
- Docker Hub (enabled by default)

### 3. `.github/workflows/scheduled.yml` - Scheduled Health Checks
Runs daily at 2 AM UTC and weekly on Sundays.

**Jobs:**
- **nightly-tests**: Full test suite
- **performance-tests**: Performance benchmarks
- **database-check**: Migration validation
- **dependency-update-check**: Security audit of dependencies

## 🔐 Required GitHub Secrets

Add these to GitHub repository settings (`Settings > Secrets and variables > Actions`):

### For Docker Deployment:
```
DOCKER_USERNAME      # Docker Hub username
DOCKER_PASSWORD      # Docker Hub access token
```

### For Heroku (optional):
```
HEROKU_API_KEY       # Heroku API token
HEROKU_APP_NAME      # Heroku app name
```

### For AWS (optional):
```
AWS_ACCESS_KEY_ID    # AWS access key
AWS_SECRET_ACCESS_KEY # AWS secret key
AWS_REGION           # AWS region (e.g., us-east-1)
EB_ENVIRONMENT       # Elastic Beanstalk environment name
```

### For Railway (optional):
```
RAILWAY_TOKEN        # Railway auth token
RAILWAY_PROJECT_ID   # Railway project ID
```

## 🏃 Running Tests Locally

### Option 1: Using pytest directly
```bash
cd backend
python -m pytest users/tests/ -v
```

### Option 2: Using docker-compose
```bash
docker-compose up -d
docker-compose exec backend python -m pytest users/tests/ -v
```

### Option 3: With coverage
```bash
cd backend
python -m pytest users/tests/ -v --cov=users --cov-report=html
open htmlcov/index.html
```

## 🐳 Docker Setup

### Development
```bash
docker-compose up -d
# Backend runs on http://localhost:8000
# Database: postgresql://postgres:postgres@db:5432/mobilemechanic
# Redis: redis://redis:6379
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
# Backend runs behind Nginx on port 80/443
```

## 📊 Test Coverage

Current test coverage:
- **81/87 tests passing** (93% success rate)
- **4 xfailed** (expected failures for SQLite)
- **2 edge cases** (architectural conflicts)

Coverage report available after each CI run:
1. Go to Actions tab
2. Click latest workflow run
3. Download coverage artifact
4. Open `htmlcov/index.html` in browser

## 🔄 Deployment Flow

```
Push to main
    ↓
Run CI Tests ─→ Fail? → Block deployment
    ↓ Pass
Build Docker Image
    ↓
Push to Docker Hub
    ↓
Deploy to production
    ↓
Run migrations
    ↓
✅ Live!
```

## 📝 Environment Variables

### Development (`.env`)
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:postgres@db:5432/mobilemechanic
CACHE_URL=redis://redis:6379/0
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (`.env.prod`)
```
DEBUG=False
SECRET_KEY=your-production-secret
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@db:5432/mobilemechanic
CACHE_URL=redis://:password@redis:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🚨 Common Issues & Fixes

### Issue: "Tests fail in CI but pass locally"
**Solution:**
- Check Python version differences
- Ensure all dependencies in `requirements.txt`
- Database isolation: CI uses in-memory SQLite

### Issue: "Deployment fails with 'Secret not found'"
**Solution:**
- Add missing secrets to GitHub Settings
- Verify secret names exactly match workflow file

### Issue: "Docker image too large"
**Solution:**
- Use multi-stage builds
- Remove development dependencies in production
- Clean up cache in Docker layers

## 📖 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Django Testing Guide](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)

## ✅ Pre-commit Hooks (Recommended)

Install pre-commit to run checks before committing:

```bash
pip install pre-commit
pre-commit install
```

Then create `.pre-commit-config.yaml` in root:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/isort/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

## 🎯 Next Steps

1. ✅ Add secrets to GitHub repo
2. ✅ Push a test commit to trigger CI
3. ✅ Monitor Actions tab for results
4. ✅ Set up production deployment
5. ✅ Configure monitoring/alerts (optional)

---

**Last Updated**: May 4, 2026
