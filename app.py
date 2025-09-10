import os
import logging
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="JurisBrain Legal Knowledge API",
    description="AI-powered legal document search and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
DB_PATH = os.getenv("DB_PATH", "legal_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_books")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
TOKENS_FILE = os.getenv("TOKENS_FILE", "api_tokens.json")

# Initialize Google AI
if GOOGLE_AI_API_KEY:
    genai.configure(api_key=GOOGLE_AI_API_KEY)

# Sample legal documents for immediate functionality
SAMPLE_DOCUMENTS = [
    {
        "id": "sample_1",
        "content": "The Constitution of India is the supreme law of India. It lays down the framework defining fundamental political principles, establishes the structure, procedures, powers and duties of government institutions and sets out fundamental rights, directive principles and the duties of citizens.",
        "metadata": {"source": "Constitution of India", "type": "constitutional_law"}
    },
    {
        "id": "sample_2", 
        "content": "Contract law is a body of law that governs, and is binding upon, the parties entering into contracts. It covers areas such as the nature of contractual obligations, breach of contract, the law of obligations and property law.",
        "metadata": {"source": "Contract Law", "type": "contract_law"}
    },
    {
        "id": "sample_3",
        "content": "Criminal law is the body of law that relates to crime. It proscribes conduct perceived as threatening, harmful, or otherwise endangering to the property, health, safety, and moral welfare of people.",
        "metadata": {"source": "Criminal Law", "type": "criminal_law"}
    }
]

# Token management functions
def load_tokens() -> Dict[str, Dict]:
    """Load API tokens from file"""
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        return {}

def save_tokens(tokens: Dict[str, Dict]):
    """Save API tokens to file"""
    try:
        with open(TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save tokens: {e}")

def generate_api_token(name: str, email: str) -> str:
    """Generate a new API token"""
    token = f"jb_{secrets.token_urlsafe(32)}"
    tokens = load_tokens()
    
    tokens[token] = {
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "usage_count": 0,
        "is_active": True
    }
    
    save_tokens(tokens)
    return token

def validate_token(token: str) -> Optional[Dict]:
    """Validate an API token"""
    if not token:
        return None
    
    tokens = load_tokens()
    token_data = tokens.get(token)
    
    if not token_data or not token_data.get("is_active", False):
        return None
    
    # Update usage statistics
    token_data["last_used"] = datetime.now().isoformat()
    token_data["usage_count"] = token_data.get("usage_count", 0) + 1
    save_tokens(tokens)
    
    return token_data

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract token from Authorization header"""
    if not authorization:
        return None
    
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization

# Pydantic models
class SearchRequest(BaseModel):
    """Request model for legal document search"""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    limit: int = Field(default=5, description="Maximum number of results", ge=1, le=20)
    include_metadata: bool = Field(default=True, description="Include document metadata")

class SearchResponse(BaseModel):
    """Response model for legal document search"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    sources: List[str]

class TokenRequest(BaseModel):
    """Request model for API token generation"""
    name: str = Field(..., description="Your name", min_length=1, max_length=100)
    email: str = Field(..., description="Your email address", min_length=1, max_length=100)

class TokenResponse(BaseModel):
    """Response model for API token generation"""
    token: str = Field(..., description="Generated API token")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    created_at: str = Field(..., description="Token creation timestamp")
    usage_instructions: Dict[str, str] = Field(..., description="Instructions for using the token")

# Dependency for optional token validation
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from token (optional for now)"""
    token = get_token_from_header(authorization)
    if token:
        user_data = validate_token(token)
        if user_data:
            return user_data
    return None

# Simple text-based search function
def simple_text_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Simple text-based search through sample documents"""
    query_lower = query.lower()
    results = []
    
    for doc in SAMPLE_DOCUMENTS:
        content_lower = doc["content"].lower()
        score = 0
        
        # Exact phrase match
        if query_lower in content_lower:
            score += 100
        
        # Word matches
        query_words = query_lower.split()
        content_words = content_lower.split()
        
        for word in query_words:
            if word in content_words:
                score += 10
            elif any(word in cword for cword in content_words):
                score += 5
        
        if score > 0:
            results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": score
            })
    
    # Sort by score and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

# Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "JurisBrain Legal Knowledge API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "search": "/search",
            "sources": "/sources", 
            "stats": "/stats",
            "health": "/health",
            "generate_token": "/generate-token",
            "token_dashboard": "/token-dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/search", response_model=SearchResponse)
async def search_legal_documents(request: SearchRequest, current_user: Optional[Dict] = Depends(get_current_user)):
    """
    Search legal documents using text-based similarity
    """
    try:
        logger.info(f"Search query: {request.query}")
        
        # Perform simple text search
        results = simple_text_search(request.query, request.limit)
        
        # Extract sources
        sources = list(set([doc["metadata"]["source"] for doc in results]))
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Search operation failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")

@app.get("/sources")
async def get_sources():
    """Get available legal document sources"""
    try:
        sources = list(set([doc["metadata"]["source"] for doc in SAMPLE_DOCUMENTS]))
        return {"sources": sources, "total": len(sources)}
    except Exception as e:
        logger.error(f"Failed to retrieve sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sources")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        return {
            "total_documents": len(SAMPLE_DOCUMENTS),
            "sources": len(set([doc["metadata"]["source"] for doc in SAMPLE_DOCUMENTS])),
            "types": len(set([doc["metadata"]["type"] for doc in SAMPLE_DOCUMENTS])),
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"Failed to retrieve statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@app.post("/generate-token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Generate a new API token for accessing the JurisBrain API
    """
    try:
        token = generate_api_token(request.name, request.email)
        return TokenResponse(
            token=token,
            name=request.name,
            email=request.email,
            created_at=datetime.now().isoformat(),
            usage_instructions={
                "header": "Authorization: Bearer " + token,
                "curl_example": f'curl -H "Authorization: Bearer {token}" -X POST "https://jurisbrainapi.onrender.com/search" -H "Content-Type: application/json" -d \'{{"query": "fundamental rights", "limit": 3}}\'',
                "python_example": f'headers = {{"Authorization": "Bearer {token}"}}\nresponse = requests.post("https://jurisbrainapi.onrender.com/search", headers=headers, json={{"query": "constitutional law"}})',
                "javascript_example": f'fetch("https://jurisbrainapi.onrender.com/search", {{\n  method: "POST",\n  headers: {{"Authorization": "Bearer {token}", "Content-Type": "application/json"}},\n  body: JSON.stringify({{"query": "contract law"}})\n}})'
            }
        )
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate token")

@app.get("/token-dashboard", response_class=HTMLResponse)
async def token_dashboard():
    """
    Simple HTML dashboard for token management
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JurisBrain API - Token Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="email"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 4px; }
            .token { font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 4px; word-break: break-all; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>JurisBrain API Token Generator</h1>
            <p>Generate an API token to access the JurisBrain Legal Knowledge API</p>
            
            <form id="tokenForm">
                <div class="form-group">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <button type="submit">Generate Token</button>
            </form>
            
            <div id="result" class="result" style="display: none;">
                <h3>Your API Token:</h3>
                <div id="token" class="token"></div>
                <h4>Usage Instructions:</h4>
                <div id="instructions"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('tokenForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = {
                    name: formData.get('name'),
                    email: formData.get('email')
                };
                
                try {
                    const response = await fetch('/generate-token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        document.getElementById('token').textContent = result.token;
                        document.getElementById('instructions').innerHTML = `
                            <p><strong>Header:</strong> ${result.usage_instructions.header}</p>
                            <p><strong>cURL Example:</strong></p>
                            <pre>${result.usage_instructions.curl_example}</pre>
                            <p><strong>Python Example:</strong></p>
                            <pre>${result.usage_instructions.python_example}</pre>
                        `;
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert('Failed to generate token. Please try again.');
                    }
                } catch (error) {
                    alert('Error generating token: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🚀 Starting JurisBrain Legal Knowledge API...")
    logger.info("📚 Using sample legal documents for immediate functionality")
    logger.info("✅ API ready with sample data")
    
    if GOOGLE_AI_API_KEY:
        logger.info("🤖 AI service available (optional)")
    else:
        logger.info("⚠️ Google AI API key not configured - using text-based search only")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)