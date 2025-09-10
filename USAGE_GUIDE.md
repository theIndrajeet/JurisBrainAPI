# 🏛️ JurisBrain Legal Knowledge API - Public Usage Guide

## 🌐 **API Endpoint**
```
https://jurisbrainapi.onrender.com
```

## 📚 **What is JurisBrain API?**
JurisBrain is a **free, open-source Legal Knowledge API** that provides access to a comprehensive database of Indian legal documents, books, and case law. It features an **AI-free text search engine** that doesn't require any API keys or external dependencies.

## 🚀 **Quick Start**

### **1. Interactive Documentation**
Visit the live API documentation: **[https://jurisbrainapi.onrender.com/docs](https://jurisbrainapi.onrender.com/docs)**

### **2. Health Check**
```bash
curl https://jurisbrainapi.onrender.com/health
```

### **3. Basic Search**
```bash
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights", "limit": 5}'
```

## 📖 **API Endpoints**

### **🔍 Search Legal Documents**
**POST** `/search`

Search through legal documents using natural language queries.

**Request Body:**
```json
{
  "query": "your legal question or topic",
  "limit": 5,
  "book_filter": "optional book name filter"
}
```

**Response:**
```json
{
  "query": "fundamental rights",
  "results": [
    {
      "content": "Fundamental Rights are basic human freedoms...",
      "metadata": {
        "source": "Constitution_of_India.pdf",
        "book": "Constitution of India",
        "author": "Constituent Assembly",
        "category": "Constitutional Law",
        "page": 12
      },
      "score": 54.0
    }
  ],
  "total_results": 1,
  "sources": ["Constitution_of_India.pdf"]
}
```

### **📚 Get Available Sources**
**GET** `/sources`

Get a list of all available legal documents and books.

**Response:**
```json
{
  "sources": [
    {
      "source": "Constitution_of_India.pdf",
      "book": "Constitution of India",
      "category": "Constitutional Law",
      "document_count": 150
    }
  ],
  "total_sources": 25
}
```

### **📊 Get Database Statistics**
**GET** `/stats`

Get statistics about the legal database.

**Response:**
```json
{
  "total_documents": 1593,
  "total_sources": 25,
  "categories": [
    "Constitutional Law",
    "Criminal Law",
    "Contract Law",
    "Tort Law"
  ],
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### **🔍 Search Specific Book**
**POST** `/search`

Search within a specific legal book or document.

```json
{
  "query": "contract formation",
  "limit": 3,
  "book_filter": "Indian Contract Act"
}
```

## 💻 **Usage Examples**

### **Python Example**
```python
import requests

# Search for legal information
def search_legal_docs(query, limit=5):
    url = "https://jurisbrainapi.onrender.com/search"
    payload = {
        "query": query,
        "limit": limit
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Example usage
results = search_legal_docs("fundamental rights")
print(f"Found {results['total_results']} results")
for result in results['results']:
    print(f"- {result['metadata']['book']}: {result['content'][:100]}...")
```

### **JavaScript Example**
```javascript
// Search for legal information
async function searchLegalDocs(query, limit = 5) {
    const response = await fetch('https://jurisbrainapi.onrender.com/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            limit: limit
        })
    });
    
    return await response.json();
}

// Example usage
searchLegalDocs("constitutional law")
    .then(results => {
        console.log(`Found ${results.total_results} results`);
        results.results.forEach(result => {
            console.log(`- ${result.metadata.book}: ${result.content.substring(0, 100)}...`);
        });
    });
```

### **cURL Examples**
```bash
# Search for fundamental rights
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights", "limit": 3}'

# Search for contract law
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "contract formation", "limit": 5}'

# Search in specific book
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "tort liability", "book_filter": "Law of Torts", "limit": 3}'

# Get available sources
curl https://jurisbrainapi.onrender.com/sources

# Get database statistics
curl https://jurisbrainapi.onrender.com/stats
```

## 🎯 **Use Cases**

### **1. Legal Research**
- Search for specific legal concepts
- Find relevant case law
- Research constitutional provisions

### **2. AI Chatbot Integration**
- Use as a knowledge base for legal chatbots
- Provide accurate legal information
- Build legal Q&A systems

### **3. Legal Education**
- Access comprehensive legal materials
- Study different areas of law
- Research legal precedents

### **4. Legal Tech Applications**
- Build legal document analysis tools
- Create legal search engines
- Develop legal research assistants

## 🔧 **Advanced Features**

### **Intelligent Text Search**
- **Exact Phrase Matching**: Finds exact legal terms
- **Semantic Understanding**: "tort" matches "civil wrong"
- **Category Bonuses**: Constitutional law gets higher scores
- **Legal Term Recognition**: Understands legal synonyms

### **No API Keys Required**
- Completely free to use
- No registration needed
- No rate limits
- No external dependencies

### **Comprehensive Legal Database**
- Indian Constitution
- Criminal Law (IPC)
- Contract Law
- Tort Law
- And many more legal documents

## 🚨 **Important Notes**

1. **Free Tier**: This API runs on Render's free tier and may spin down after inactivity
2. **Response Time**: First request after inactivity may take 30-60 seconds
3. **No Rate Limits**: Use responsibly
4. **Open Source**: Code available at [GitHub](https://github.com/theIndrajeet/JurisBrainAPI)

## 🤝 **Contributing**

- **GitHub**: [https://github.com/theIndrajeet/JurisBrainAPI](https://github.com/theIndrajeet/JurisBrainAPI)
- **Issues**: Report bugs or request features
- **Pull Requests**: Contribute improvements
- **Documentation**: Help improve this guide

## 📞 **Support**

- **GitHub Issues**: For technical support
- **Documentation**: Check `/docs` endpoint
- **Community**: Join discussions on GitHub

---

**🏛️ JurisBrain Legal Knowledge API - Making Legal Information Accessible to Everyone**
