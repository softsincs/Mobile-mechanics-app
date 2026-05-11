# 🤝 Contributing to MobileMechanic

Thank you for your interest in contributing to MobileMechanic! This document provides guidelines and instructions for contributing to the project.

## 📋 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Report issues responsibly
- Focus on collaboration

## 🚀 Getting Started

### 1. Fork the Repository
```bash
git clone https://github.com/yourusername/MobileMechanic.git
cd MobileMechanic
```

### 2. Setup Development Environment
```bash
make setup
cp .env.example .env
# Update .env with your configuration
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

## 💻 Development Workflow

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest users/tests/test_auth_login.py -v

# Run specific test
pytest users/tests/test_auth_login.py::TestLogin::test_login_success -v
```

### Code Quality
```bash
# Lint code
make lint

# Format code
make format

# Sort imports
make sort-imports

# Run all checks
make quality

# Security check
make security
```

### Database
```bash
# Create migrations
make migrations

# Run migrations
make migrate

# Reset database (WARNING: deletes data)
python manage.py migrate zero
make migrate
```

## 📝 Commit Messages

Follow conventional commit format:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `security`: Security fixes

**Examples:**
```
feat(auth): add two-factor authentication
fix(otp): resolve token expiry validation bug
docs(readme): update installation instructions
test(auth): add comprehensive OTP tests
```

## 🧪 Testing Requirements

- Write tests for new features
- Update existing tests when modifying behavior
- Aim for >90% code coverage
- All tests must pass before PR submission

### Test File Structure
```python
@pytest.mark.django_db
class TestFeatureName:
    """Test description."""
    
    def test_specific_behavior(self, fixture1, fixture2):
        """Test specific behavior with setup and assertions."""
        # Arrange
        data = {"key": "value"}
        
        # Act
        response = client.post("/api/v1/endpoint/", data)
        
        # Assert
        assert response.status_code == 200
```

## 📦 Pull Request Process

1. **Update Tests & Documentation**
   - Add/update tests for your changes
   - Update README if needed
   - Document new features

2. **Run Quality Checks**
   ```bash
   make quality    # Run all checks
   make test       # Run tests
   ```

3. **Create Pull Request**
   - Use the PR template
   - Describe changes clearly
   - Link related issues
   - Request reviewers

4. **Address Review Comments**
   - Push new commits to the same branch
   - Respond to feedback
   - Update PR description if needed

5. **Merge**
   - Ensure all checks pass
   - Squash commits if needed
   - Merge to main

## 🔍 Code Review Checklist

Reviewers will check:

- [ ] Code follows project style guide
- [ ] Tests cover new functionality
- [ ] No breaking changes (or documented)
- [ ] Documentation updated
- [ ] Linting passes
- [ ] Security vulnerabilities addressed
- [ ] Performance impact considered
- [ ] Database migrations compatible

## 📚 Documentation

### Updating Docs
- Docstrings for all functions/classes
- Comments for complex logic
- README for new features
- CI_CD_GUIDE.md for process changes

### Docstring Format
```python
def create_otp_token(user, purpose="login", expiry_minutes=5):
    """
    Create an OTP token for user verification.
    
    Args:
        user (User): The user object
        purpose (str): Purpose of OTP (login, verification, reset)
        expiry_minutes (int): Token expiry time in minutes
    
    Returns:
        tuple: (otp_token_object, otp_code_string)
    
    Raises:
        ValueError: If purpose is invalid
        User.DoesNotExist: If user not found
    
    Example:
        >>> token, code = create_otp_token(user, "login")
        >>> print(code)  # "123456"
    """
```

## 🐛 Reporting Issues

When reporting bugs:

1. **Use Issue Template**
   - Title: Brief description
   - Environment: OS, Python version, Django version
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs

2. **Label Issues**
   - `bug`: Bug reports
   - `feature`: Feature requests
   - `question`: Questions
   - `documentation`: Doc improvements

## 📌 Project Structure

```
MobileMechanic/
├── backend/
│   ├── mobilemechanic/    # Project config
│   ├── users/             # Auth app (main focus)
│   ├── manage.py
│   └── requirements.txt
├── .github/
│   ├── workflows/         # CI/CD workflows
│   └── pull_request_template.md
├── docker-compose.yml
├── Makefile
└── CI_CD_GUIDE.md
```

## 🎯 Priority Areas

Current focus areas for contributions:

1. **Testing** - Improve test coverage
2. **Documentation** - Enhance API docs
3. **Performance** - Optimize database queries
4. **Security** - Security improvements
5. **Features** - New functionality

## 💡 Tips for Contributors

1. **Start Small** - Begin with documentation or small fixes
2. **Ask Questions** - Don't hesitate to ask in issues/discussions
3. **Test Everything** - Run the full test suite before submitting
4. **Keep PRs Focused** - One feature/fix per PR
5. **Update Often** - Stay in sync with main branch

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Docs](https://docs.github.com/actions)

## ❓ Questions?

- Open an issue for bugs
- Start a discussion for questions
- Check existing issues/PRs first
- Join our community discussions

---

**Thank you for contributing to MobileMechanic! 🚀**
