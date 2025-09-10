# Contributing to JurisBrain Legal Knowledge API

Thank you for your interest in contributing to JurisBrain! This document provides guidelines and information for contributors.

## 🎯 **Ways to Contribute**

- 🐛 **Bug Reports**: Found a bug? Let us know!
- 💡 **Feature Requests**: Have an idea? We'd love to hear it!
- 📖 **Documentation**: Help improve our docs
- 🧪 **Testing**: Write tests or test new features
- 🔧 **Code**: Submit bug fixes or new features
- 🌐 **Translation**: Help with internationalization
- 📚 **Legal Content**: Suggest new legal document sources

## 🚀 **Getting Started**

### **Development Setup**

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/JurisBrainAPI.git
   cd JurisBrainAPI
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest black isort flake8 pre-commit
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Tests**
   ```bash
   pytest
   ```

6. **Start Development Server**
   ```bash
   python app.py
   ```

### **Development Workflow**

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

2. **Make Your Changes**
   - Write clean, readable code
   - Follow Python PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check app.py
   isort --check-only app.py
   flake8 app.py
   
   # Run examples to ensure they work
   python examples/python_example.py
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new search filter functionality"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 📝 **Coding Standards**

### **Code Style**

- **Python**: Follow PEP 8
- **Line Length**: 88 characters (Black default)
- **Imports**: Use isort for import organization
- **Type Hints**: Use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings

### **Example Code Style**

```python
from typing import List, Dict, Any, Optional

async def search_documents(
    query: str, 
    limit: int = 5, 
    book_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search legal documents using semantic similarity.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        book_filter: Optional filter for specific books
        
    Returns:
        Dictionary containing search results
        
    Raises:
        HTTPException: If search fails
    """
    # Implementation here
    pass
```

### **Commit Message Format**

Use conventional commits:

```
type(scope): description

Examples:
feat: add book search functionality
fix: resolve database connection issue  
docs: update API documentation
test: add unit tests for search endpoint
refactor: improve error handling
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

## 🧪 **Testing Guidelines**

### **Writing Tests**

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test API endpoints
3. **Example Tests**: Ensure examples work correctly

### **Test Structure**

```python
import pytest
from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_endpoint():
    """Test search functionality."""
    response = client.post("/search", json={
        "query": "test query",
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_results" in data
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_search.py

# Run specific test
pytest tests/test_search.py::test_search_endpoint
```

## 📖 **Documentation Guidelines**

### **API Documentation**

- Use FastAPI's automatic documentation features
- Add detailed descriptions to endpoints
- Include example requests and responses
- Document error cases

### **Code Documentation**

- Write clear docstrings for all functions
- Include type hints
- Document complex logic with comments
- Update README for new features

### **Example Documentation**

```python
@app.post("/search", response_model=SearchResponse)
async def search_legal_documents(request: SearchRequest):
    """
    Search legal documents using semantic similarity.
    
    This endpoint performs AI-powered semantic search across the entire 
    legal document database. It understands legal terminology and context
    to find the most relevant documents.
    
    **Example queries:**
    - "What is Section 498A of IPC?"
    - "Fundamental rights under Indian Constitution"
    - "Contract law essentials"
    """
```

## 🐛 **Bug Reports**

### **Before Reporting**

1. Check existing issues
2. Update to latest version
3. Test with minimal example
4. Check documentation

### **Bug Report Template**

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.11.0]
- API Version: [e.g., 1.0.0]
- Docker: [Yes/No]

**Additional Context**
Any other relevant information
```

## 💡 **Feature Requests**

### **Feature Request Template**

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other ways to solve this problem

**Additional Context**
Any other relevant information
```

## 🔧 **Development Areas**

### **High Priority**

- 🚀 **Performance Optimization**: Improve search speed
- 🔐 **Security**: Add authentication and rate limiting
- 📊 **Analytics**: Usage tracking and metrics
- 🧪 **Testing**: Increase test coverage

### **Medium Priority**

- 🌐 **Internationalization**: Support for other legal systems
- 📱 **Mobile Support**: Mobile-optimized responses
- 🔍 **Advanced Search**: Filters, sorting, faceted search
- 📈 **Monitoring**: Health checks and alerting

### **Low Priority**

- 🎨 **UI**: Web interface for the API
- 📚 **More Content**: Additional legal document sources
- 🤖 **AI Features**: Advanced NLP capabilities
- 📦 **Packaging**: PyPI package distribution

## 🏆 **Recognition**

Contributors will be:

- 📝 **Listed** in the README
- 🏷️ **Tagged** in release notes
- 🎉 **Celebrated** in community discussions
- 🌟 **Featured** on social media (with permission)

## 📞 **Getting Help**

- 💬 **GitHub Discussions**: For questions and ideas
- 🐛 **GitHub Issues**: For bugs and feature requests
- 📧 **Email**: support@jurisbrain.com for private matters

## 📜 **Code of Conduct**

### **Our Standards**

- ✅ **Be respectful** and inclusive
- ✅ **Be constructive** in feedback
- ✅ **Be patient** with newcomers
- ✅ **Be collaborative** and helpful
- ❌ **No harassment** or discrimination
- ❌ **No spam** or off-topic content

### **Enforcement**

Violations may result in:
1. **Warning**: First offense
2. **Temporary Ban**: Repeated violations
3. **Permanent Ban**: Serious violations

## 🎉 **Thank You!**

Every contribution, no matter how small, helps make JurisBrain better for everyone. Thank you for being part of our community!

---

**Questions?** Feel free to ask in [GitHub Discussions](https://github.com/theIndrajeet/JurisBrainAPI/discussions) or email us at support@jurisbrain.com.
