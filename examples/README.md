# JurisBrain API Examples

This directory contains comprehensive examples showing how to use the JurisBrain Legal Knowledge API in different programming languages and environments.

## 📁 Available Examples

### 1. Python Example (`python_example.py`)
- **Requirements**: `pip install requests`
- **Features**:
  - Complete Python client class
  - Health checks and statistics
  - Basic and book-specific search
  - Interactive search mode
  - Error handling and pretty printing

**Usage:**
```bash
# Run all examples
python examples/python_example.py

# Interactive mode
python examples/python_example.py interactive
```

### 2. JavaScript Example (`javascript_example.js`)
- **Requirements**: `npm install axios` (for Node.js)
- **Features**:
  - Works in both Node.js and browser
  - Async/await pattern
  - Interactive web interface
  - Error handling and formatting

**Usage:**
```bash
# Node.js
node examples/javascript_example.js

# Browser - include in HTML:
<script src="examples/javascript_example.js"></script>
```

### 3. cURL Examples (`curl_examples.sh`)
- **Requirements**: `curl`, `python3` (for JSON formatting)
- **Features**:
  - All API endpoints covered
  - Interactive mode
  - Batch processing
  - Error handling examples
  - Advanced usage patterns

**Usage:**
```bash
# Make executable
chmod +x examples/curl_examples.sh

# Run interactively
./examples/curl_examples.sh

# Run specific examples
./examples/curl_examples.sh health
./examples/curl_examples.sh search
./examples/curl_examples.sh interactive
```

## 🚀 Quick Start

1. **Start the API**:
   ```bash
   # Using Docker
   docker-compose up
   
   # Or directly
   python app.py
   ```

2. **Choose your language**:
   - **Python**: `python examples/python_example.py`
   - **JavaScript**: `node examples/javascript_example.js`
   - **cURL**: `./examples/curl_examples.sh`

3. **Try interactive mode** for hands-on testing:
   ```bash
   python examples/python_example.py interactive
   # or
   ./examples/curl_examples.sh interactive
   ```

## 📖 Common Usage Patterns

### Basic Search
```python
# Python
client = JurisBrainClient()
results = client.search("fundamental rights under Indian Constitution")

# JavaScript
const client = new JurisBrainClient();
const results = await client.search("fundamental rights under Indian Constitution");

# cURL
curl -X POST 'http://localhost:8000/search' \
  -H 'Content-Type: application/json' \
  -d '{"query": "fundamental rights under Indian Constitution", "limit": 5}'
```

### Book-Specific Search
```python
# Python
results = client.search_by_book("tort liability", "RK Bangia")

# JavaScript
const results = await client.searchByBook("tort liability", "RK Bangia");

# cURL
curl -X POST 'http://localhost:8000/search-by-book' \
  -H 'Content-Type: application/json' \
  -d '{"query": "tort liability", "book_filter": "RK Bangia", "limit": 5}'
```

### Health Check
```python
# Python
health = client.health_check()
print(f"Status: {health['status']}")

# JavaScript
const health = await client.healthCheck();
console.log(`Status: ${health.status}`);

# cURL
curl -X GET 'http://localhost:8000/health'
```

## 🔧 Integration Examples

### Web Application Integration
```javascript
// Frontend JavaScript
const searchButton = document.getElementById('search');
const resultsDiv = document.getElementById('results');

searchButton.addEventListener('click', async () => {
    const query = document.getElementById('query').value;
    const client = new JurisBrainClient();
    
    try {
        const results = await client.search(query);
        displayResults(results);
    } catch (error) {
        resultsDiv.innerHTML = `Error: ${error.message}`;
    }
});
```

### Python Script Integration
```python
#!/usr/bin/env python3
import sys
from examples.python_example import JurisBrainClient

def search_legal_topic(topic):
    client = JurisBrainClient()
    try:
        results = client.search(topic, limit=10)
        return results['results']
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        results = search_legal_topic(topic)
        for result in results:
            print(f"Source: {result['source']}")
            print(f"Content: {result['content'][:200]}...")
            print("-" * 40)
```

### Shell Script Integration
```bash
#!/bin/bash
# legal_search.sh - Quick legal search script

QUERY="$1"
API_URL="http://localhost:8000"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 'your legal question'"
    exit 1
fi

curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$QUERY\", \"limit\": 3}" | \
    python3 -m json.tool
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: Failed to connect to localhost:8000
   ```
   **Solution**: Make sure the API is running:
   ```bash
   docker-compose up
   # or
   python app.py
   ```

2. **503 Service Unavailable**
   ```
   Error: AI service not configured
   ```
   **Solution**: Set your Google AI API key:
   ```bash
   export GOOGLE_AI_API_KEY="your_api_key_here"
   ```

3. **422 Validation Error**
   ```
   Error: Query too long or invalid parameters
   ```
   **Solution**: Check query length (max 500 chars) and limit (max 20)

4. **Python Import Error**
   ```
   ModuleNotFoundError: No module named 'requests'
   ```
   **Solution**: Install required packages:
   ```bash
   pip install requests
   ```

### Debug Mode

Enable verbose output in examples:

```bash
# Python - add debug parameter
python examples/python_example.py --debug

# cURL - use verbose flag
curl -v -X GET 'http://localhost:8000/health'
```

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Statistics**: http://localhost:8000/stats

## 🤝 Contributing

Found an issue or want to add more examples? Please:

1. Fork the repository
2. Create a feature branch
3. Add your example with proper documentation
4. Submit a pull request

## 📄 License

These examples are part of the JurisBrain Legal Knowledge API project and are licensed under the MIT License.
