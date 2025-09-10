# 🏛️ JurisBrain Legal Knowledge API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

> **Free & Open Source Legal Knowledge API** - Access comprehensive Indian legal documents with AI-powered semantic search

## 🎯 **What is JurisBrain?**

JurisBrain is a **free and open-source Legal Knowledge API** that provides developers with access to a comprehensive database of **2.6+ million legal document chunks** covering Indian law. Built with modern AI technology, it offers semantic search capabilities that understand legal terminology and context.

### ✨ **Key Features**

- 🔍 **Semantic Search** - AI-powered understanding of legal queries
- 📚 **Comprehensive Coverage** - 2.6M+ legal document chunks
- 🏛️ **Multiple Legal Areas** - Constitutional, Criminal, Family, Contract, Tort, Property Law
- 📖 **Book-Specific Search** - Search within specific legal texts or by author
- 🚀 **High Performance** - Built with FastAPI for speed and scalability
- 🐳 **Docker Ready** - Easy deployment with Docker and Docker Compose
- 🔓 **Free & Open Source** - MIT License, no API keys required for basic usage
- 📊 **RESTful API** - Clean, well-documented endpoints
- 🌐 **CORS Enabled** - Ready for web applications

### 🏛️ **Legal Coverage**

| Area | Coverage | Examples |
|------|----------|----------|
| **Constitutional Law** | Fundamental Rights, DPSP, Constitutional Amendments | Articles 19, 21, 32 |
| **Criminal Law** | IPC, CrPC, Evidence Act | Sections 498A, 302, 420 |
| **Family Law** | Marriage, Divorce, Adoption, Succession | Hindu Marriage Act, Muslim Personal Law |
| **Contract Law** | Indian Contract Act, Commercial Law | Essential elements, Breach of contract |
| **Tort Law** | Negligence, Defamation, Nuisance | Liability principles, Damages |
| **Property Law** | Transfer of Property, Registration | Sale, Mortgage, Lease |

## 🌐 **Live API**

**Ready to use right now!** No setup required:

- **🌐 API Endpoint**: `https://jurisbrainapi.onrender.com`
- **📖 Interactive Docs**: [https://jurisbrainapi.onrender.com/docs](https://jurisbrainapi.onrender.com/docs)
- **🎮 Demo Page**: Open `demo.html` in your browser
- **🐍 Python Client**: Use `jurisbrain_client.py`

### **Quick Test**
```bash
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights", "limit": 3}'
```

## 🚀 **Local Setup (Optional)**

### **Option 1: Docker (Recommended)**

```bash
# 1. Clone the repository
git clone https://github.com/theIndrajeet/JurisBrainAPI.git
cd JurisBrainAPI

# 2. Set up environment
cp .env.example .env
# Edit .env and add your Google AI API key (optional)

# 3. Start with Docker Compose
docker-compose up --build

# 4. API is ready at http://localhost:8000
```

### **Option 2: Local Installation**

```bash
# 1. Clone and setup
git clone https://github.com/theIndrajeet/JurisBrainAPI.git
cd JurisBrainAPI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your configuration

# 5. Run the API
python app.py

# 6. API is ready at http://localhost:8000
```

### **Verify Installation**

```bash
# Check API health
curl http://localhost:8000/health

# View interactive documentation
open http://localhost:8000/docs
```

## 📖 **API Usage**

### **Basic Search**

Search across all legal documents:

```bash
# Using the live API
curl -X POST "https://jurisbrainapi.onrender.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights under Indian Constitution", "limit": 5}'

# Or locally
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights under Indian Constitution", "limit": 5}'
```

### **Book-Specific Search**

Search within specific legal texts:

```bash
curl -X POST "http://localhost:8000/search-by-book" \
  -H "Content-Type: application/json" \
  -d '{"query": "tort liability", "book_filter": "RK Bangia", "limit": 5}'
```

### **Get Database Statistics**

```bash
curl http://localhost:8000/stats
```

### **List Available Sources**

```bash
curl "http://localhost:8000/sources?limit=20"
```

## 🛠️ **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message and basic info |
| `/health` | GET | API health status |
| `/stats` | GET | Database statistics |
| `/search` | POST | Semantic search across all documents |
| `/search-by-book` | POST | Search within specific books/authors |
| `/sources` | GET | List available legal document sources |
| `/docs` | GET | Interactive API documentation |

## 💻 **Client Examples**

### **Python**

```python
import requests

# Search for legal information using the live API
response = requests.post("https://jurisbrainapi.onrender.com/search", json={
    "query": "Section 498A of Indian Penal Code",
    "limit": 3
})

results = response.json()
for result in results['results']:
    print(f"Source: {result['metadata']['source']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Score: {result['score']}")
    print("-" * 50)
```

### **Using the Python Client**

```python
from jurisbrain_client import JurisBrainClient

# Initialize client
client = JurisBrainClient()

# Search for legal information
results = client.search("fundamental rights", limit=3)
print(f"Found {results['total_results']} results")

# Search by category
constitutional_results = client.search_by_category("rights", "Constitutional Law")
```

### **JavaScript**

```javascript
// Using fetch API with the live API
const searchLegal = async (query) => {
    const response = await fetch('https://jurisbrainapi.onrender.com/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, limit: 5 })
    });
    
    const results = await response.json();
    return results;
};

// Usage
searchLegal("contract law essentials").then(results => {
    console.log(`Found ${results.total_results} results`);
    results.results.forEach(result => {
        console.log(`${result.metadata.source}: ${result.content.substring(0, 100)}...`);
    });
});
```

### **More Examples**

Check the [`examples/`](examples/) directory for comprehensive examples in:
- **Python** - Complete client with interactive mode
- **JavaScript** - Browser and Node.js examples
- **cURL** - Shell scripts and batch processing

## 🗂️ **Project Structure**

```
JurisBrainAPI/
├── app.py                 # Main API application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example         # Environment template
├── README.md            # This file
├── examples/            # Usage examples
│   ├── python_example.py
│   ├── javascript_example.js
│   ├── curl_examples.sh
│   └── README.md
└── legal_db/           # ChromaDB database (not in repo)
    └── ...
```

## ⚙️ **Configuration**

### **Environment Variables**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_AI_API_KEY` | Yes* | - | Google AI API key for embeddings |
| `DB_PATH` | No | `legal_db` | Path to ChromaDB database |
| `COLLECTION_NAME` | No | `law_books` | ChromaDB collection name |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |

*Required for full functionality. The API can run without it but with limited features.

### **Getting Google AI API Key**

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file:
   ```
   GOOGLE_AI_API_KEY=your_api_key_here
   ```

## 🐳 **Docker Deployment**

### **Development**

```bash
# Start development environment
docker-compose up

# With rebuild
docker-compose up --build

# Background mode
docker-compose up -d
```

### **Production**

```bash
# Production with Nginx proxy
docker-compose --profile production up -d

# With monitoring (Prometheus + Grafana)
docker-compose --profile monitoring up -d
```

### **Scaling**

```bash
# Scale API instances
docker-compose up --scale jurisbrain-api=3
```

## 🚀 **Deployment Options**

### **Cloud Platforms**

#### **Railway**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

#### **Render**
1. Fork this repository
2. Connect to Render
3. Set environment variables
4. Deploy!

#### **Heroku**
```bash
# Install Heroku CLI, then:
heroku create your-jurisbrain-api
heroku config:set GOOGLE_AI_API_KEY=your_key
git push heroku main
```

#### **DigitalOcean App Platform**
1. Fork repository
2. Create new app in DigitalOcean
3. Connect GitHub repository
4. Set environment variables
5. Deploy

### **Self-Hosted**

#### **VPS/Server**
```bash
# Clone and setup
git clone https://github.com/theIndrajeet/JurisBrainAPI.git
cd JurisBrainAPI

# Using Docker
docker-compose up -d

# Or using systemd service
sudo cp jurisbrain-api.service /etc/systemd/system/
sudo systemctl enable jurisbrain-api
sudo systemctl start jurisbrain-api
```

## 📊 **Performance & Limits**

| Metric | Value |
|--------|-------|
| **Database Size** | 2.6M+ documents |
| **Response Time** | < 500ms (typical) |
| **Concurrent Users** | 100+ (single instance) |
| **Rate Limiting** | None (configurable) |
| **Memory Usage** | ~1GB (with database loaded) |
| **Storage Required** | ~2GB (database) |

## 🤝 **Contributing**

We welcome contributions! Here's how to get started:

### **Development Setup**

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/JurisBrainAPI.git
cd JurisBrainAPI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install development dependencies
pip install -r requirements.txt
pip install pytest black isort flake8

# 4. Run tests
pytest

# 5. Format code
black app.py
isort app.py
flake8 app.py
```

### **Contribution Guidelines**

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Areas for Contribution**

- 🐛 **Bug fixes** and performance improvements
- 📚 **Documentation** and examples
- 🌐 **Internationalization** (other legal systems)
- 🔧 **New features** and API endpoints
- 🧪 **Testing** and quality assurance
- 🎨 **UI/UX** for documentation

## 🐛 **Troubleshooting**

### **Common Issues**

#### **API Not Starting**
```bash
# Check if port is in use
lsof -i :8000

# Check logs
docker-compose logs jurisbrain-api
```

#### **Database Connection Failed**
```bash
# Verify database directory exists
ls -la legal_db/

# Check permissions
chmod -R 755 legal_db/
```

#### **AI Service Not Configured**
```bash
# Verify API key is set
echo $GOOGLE_AI_API_KEY

# Check .env file
cat .env
```

### **Debug Mode**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python app.py --debug
```

### **Performance Issues**

1. **Slow responses**: Check database size and available memory
2. **High CPU usage**: Consider scaling with multiple instances
3. **Memory issues**: Monitor with `docker stats` or `htop`

## 📄 **Legal Disclaimer**

⚖️ **Important**: This API is for **educational and research purposes only**. The information provided should not be considered as legal advice. Always consult with qualified legal professionals for legal matters.

- **No Legal Advice**: This API does not provide legal advice
- **Educational Use**: Intended for learning and research
- **Accuracy**: While we strive for accuracy, information may be outdated
- **Professional Consultation**: Always consult qualified lawyers for legal matters

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### **What this means:**
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed  
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❌ **Liability** - No warranty provided
- ❌ **Patent rights** - Not granted

## 🙏 **Acknowledgments**

- **Legal Content**: Based on publicly available Indian legal documents
- **AI Technology**: Powered by Google's Generative AI
- **Vector Database**: ChromaDB for efficient similarity search
- **Web Framework**: FastAPI for high-performance API
- **Community**: Thanks to all contributors and users

## 📞 **Support & Community**

- 📧 **Email**: support@jurisbrain.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/theIndrajeet/JurisBrainAPI/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/theIndrajeet/JurisBrainAPI/discussions)
- 📖 **Documentation**: [API Docs](http://localhost:8000/docs)

## 🗺️ **Roadmap**

### **Version 1.1** (Coming Soon)
- [ ] Authentication and API keys
- [ ] Rate limiting and usage analytics
- [ ] More legal document sources
- [ ] Advanced search filters

### **Version 2.0** (Future)
- [ ] Multi-language support
- [ ] Legal citation extraction
- [ ] Case law integration
- [ ] Advanced AI features

---

<div align="center">

**Made with ❤️ for the legal community**

[🌟 Star this repo](https://github.com/theIndrajeet/JurisBrainAPI) • [🐛 Report Bug](https://github.com/theIndrajeet/JurisBrainAPI/issues) • [💡 Request Feature](https://github.com/theIndrajeet/JurisBrainAPI/issues)

</div>
