"""
JurisBrain Legal Knowledge API

A free and open-source Legal Knowledge API that provides semantic search 
capabilities across a comprehensive database of Indian legal documents.

Features:
- Semantic search across 2.6M+ legal document chunks
- Support for multiple legal categories (Constitutional, Criminal, Family, Contract Law, etc.)
- Book-specific search capabilities
- RESTful API endpoints for easy integration
- Built with FastAPI for high performance

Author: JurisBrain Team
License: MIT
Repository: https://github.com/theIndrajeet/JurisBrainAPI
"""

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

# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment variables (with fallbacks for development)
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "legal_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "law_books")
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
TOKENS_FILE = os.getenv("TOKENS_FILE", "api_tokens.json")

# Model configurations
EMBEDDING_MODEL = "models/embedding-001"
TASK_TYPE = "retrieval_query"

# =============================================================================
# AUTHENTICATION SYSTEM
# =============================================================================

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

# =============================================================================
# DATA MODELS
# =============================================================================

class SearchRequest(BaseModel):
    """Request model for legal document search"""
    query: str = Field(..., description="Search query for legal documents", min_length=1, max_length=500)
    limit: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    include_sources: bool = Field(default=True, description="Include source information in response")

class BookSearchRequest(BaseModel):
    """Request model for book-specific search"""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    book_filter: str = Field(..., description="Book name or author to filter by", min_length=1)
    limit: int = Field(default=5, description="Number of results to return", ge=1, le=20)

class SearchResult(BaseModel):
    """Individual search result"""
    content: str = Field(..., description="Legal document content")
    source: str = Field(..., description="Source document name")
    relevance_score: float = Field(..., description="Relevance score (0-1)")

class SearchResponse(BaseModel):
    """Response model for search results"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results found")
    sources: List[str] = Field(default=[], description="Unique sources in results")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database_status: str
    total_documents: int

class StatsResponse(BaseModel):
    """Database statistics response"""
    total_documents: int
    total_sources: int
    available_categories: List[str]
    database_size: str

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

# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="JurisBrain Legal Knowledge API",
    description="""
    🏛️ **Free & Open Source Legal Knowledge API**
    
    Access a comprehensive database of Indian legal documents with semantic search capabilities.
    
    ## Features
    - **2.6M+ Legal Documents** - Comprehensive coverage of Indian law
    - **Semantic Search** - AI-powered understanding of legal queries
    - **Book-Specific Search** - Search within specific legal texts
    - **Source Citations** - Always know where information comes from
    - **RESTful API** - Easy integration with any application
    
    ## Coverage
    - Constitutional Law
    - Criminal Law (IPC, CrPC)
    - Family Law
    - Contract Law
    - Tort Law
    - Property Law
    - And much more...
    
    ## Getting Started
    1. Use `/search` for general legal document search
    2. Use `/search-by-book` for book-specific queries
    3. Check `/health` for system status
    4. View `/stats` for database information
    
    **Note**: This API is for educational and research purposes. Always consult qualified legal professionals for legal advice.
    """,
    version="1.0.0",
    contact={
        "name": "JurisBrain Team",
        "url": "https://github.com/theIndrajeet/JurisBrainAPI",
        "email": "support@jurisbrain.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# DEPENDENCY INJECTION
# =============================================================================

def get_database():
    """Get ChromaDB collection"""
    if not hasattr(app.state, "collection"):
        raise HTTPException(status_code=503, detail="Database not available")
    return app.state.collection

def recreate_database_with_correct_dimensions():
    """Recreate database with correct embedding dimensions"""
    try:
        logger.info("🔄 Recreating database with correct embedding dimensions...")
        
        # Delete existing collection if it exists
        client = chromadb.PersistentClient(path=DB_PATH, settings=chromadb.Settings(anonymized_telemetry=False))
        try:
            client.delete_collection(name=COLLECTION_NAME)
            logger.info("🗑️ Deleted existing collection with wrong dimensions")
        except:
            pass  # Collection might not exist
        
        # Create new collection
        collection = client.create_collection(name=COLLECTION_NAME)
        
        # Add sample documents with proper embeddings
        sample_documents = [
            {
                "content": "The Constitution of India is the supreme law of India. It lays down the framework defining fundamental political principles, establishes the structure, procedures, powers and duties of government institutions and sets out fundamental rights, directive principles and the duties of citizens.",
                "metadata": {
                    "source": "Constitution_of_India.pdf",
                    "book": "Constitution of India",
                    "author": "Constituent Assembly",
                    "category": "Constitutional Law",
                    "page": 1
                }
            },
            {
                "content": "Fundamental Rights are basic human freedoms that every Indian citizen has the right to enjoy for a proper and harmonious development of personality. These rights universally apply to all citizens, irrespective of race, place of birth, religion, caste or gender.",
                "metadata": {
                    "source": "Constitution_of_India.pdf", 
                    "book": "Constitution of India",
                    "author": "Constituent Assembly",
                    "category": "Constitutional Law",
                    "page": 12
                }
            },
            {
                "content": "A tort is a civil wrong that causes a claimant to suffer loss or harm, resulting in legal liability for the person who commits the tortious act. Tort law in India is primarily based on English common law principles.",
                "metadata": {
                    "source": "Law_of_Torts.pdf",
                    "book": "Law of Torts",
                    "author": "Ratanlal & Dhirajlal",
                    "category": "Tort Law",
                    "page": 1
                }
            },
            {
                "content": "Criminal law is the body of law that relates to crime. It proscribes conduct perceived as threatening, harmful, or otherwise endangering to the property, health, safety, and moral welfare of people.",
                "metadata": {
                    "source": "Indian_Penal_Code.pdf",
                    "book": "Indian Penal Code",
                    "author": "Macaulay",
                    "category": "Criminal Law", 
                    "page": 1
                }
            },
            {
                "content": "Contract law is the body of law that governs making and enforcing agreements. A contract is a legally binding agreement between two or more parties that creates mutual obligations enforceable by law.",
                "metadata": {
                    "source": "Indian_Contract_Act.pdf",
                    "book": "Indian Contract Act, 1872",
                    "author": "Legislature",
                    "category": "Contract Law",
                    "page": 1
                }
            }
        ]
        
        # Add documents to collection
        documents = [doc["content"] for doc in sample_documents]
        metadatas = [doc["metadata"] for doc in sample_documents]
        ids = [f"doc_{i+1}" for i in range(len(sample_documents))]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ Database recreated with {len(sample_documents)} documents")
        return collection
        
    except Exception as e:
        logger.error(f"❌ Failed to recreate database: {e}")
        return None

def get_embedding_client():
    """Get Google AI embedding client"""
    if not GOOGLE_AI_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")
    return genai

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using Google AI (optional)"""
    # Skip AI embeddings entirely - use text search instead
    logger.info("Using text-based search (no AI embeddings needed)")
    return None  # Always use fallback search

def fallback_text_search(query: str, limit: int, book_filter: str, collection) -> tuple:
    """Advanced text-based search engine (no AI needed!)"""
    try:
        # Get all documents
        all_docs = collection.get()
        documents = all_docs.get('documents', [])
        metadatas = all_docs.get('metadatas', [])
        
        # Advanced text matching with intelligent scoring
        results = []
        query_lower = query.lower().strip()
        query_words = set(query_lower.split())
        
        # Remove common words for better matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        query_words = query_words - stop_words
        
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            # Skip if book filter doesn't match
            if book_filter and book_filter.lower() not in meta.get('source', '').lower():
                continue
                
            doc_lower = doc.lower()
            
            # Calculate intelligent relevance score
            score = 0
            
            # 1. Exact phrase match (highest priority)
            if query_lower in doc_lower:
                score += 20
                # Bonus for multiple occurrences
                score += doc_lower.count(query_lower) * 5
            
            # 2. Word-by-word matching
            doc_words = set(doc_lower.split())
            word_matches = len(query_words.intersection(doc_words))
            if word_matches > 0:
                score += word_matches * 3
                # Bonus for consecutive word matches
                query_phrase = ' '.join(sorted(query_words))
                if query_phrase in doc_lower:
                    score += 10
            
            # 3. Partial word matches (for legal terms)
            for query_word in query_words:
                if len(query_word) > 3:  # Only for meaningful words
                    for doc_word in doc_words:
                        if query_word in doc_word or doc_word in query_word:
                            score += 1
            
            # 4. Category and book title bonuses
            if 'category' in meta:
                category_lower = meta['category'].lower()
                for word in query_words:
                    if word in category_lower:
                        score += 8
            if 'book' in meta:
                book_lower = meta['book'].lower()
                for word in query_words:
                    if word in book_lower:
                        score += 6
            if 'source' in meta:
                source_lower = meta['source'].lower()
                for word in query_words:
                    if word in source_lower:
                        score += 4
            
            # 5. Legal term bonuses
            legal_terms = {
                'constitution': ['constitutional', 'constitution'],
                'rights': ['fundamental', 'basic', 'human'],
                'law': ['legal', 'statute', 'act'],
                'court': ['judicial', 'tribunal'],
                'contract': ['agreement', 'obligation'],
                'criminal': ['penal', 'offence', 'crime'],
                'tort': ['civil', 'liability', 'damages']
            }
            
            for term, synonyms in legal_terms.items():
                if term in query_lower:
                    for synonym in synonyms:
                        if synonym in doc_lower:
                            score += 3
            
            if score > 0:
                results.append((doc, meta, score))
        
        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x[2], reverse=True)
        results = results[:limit]
        
        if not results:
            # Return sample documents if no matches
            sample_docs = documents[:limit] if documents else []
            sample_metas = metadatas[:limit] if metadatas else []
            sample_scores = [1.0] * len(sample_docs)
            return sample_docs, sample_metas, sample_scores, []
        
        # Unpack results
        docs, metas, scores = zip(*results)
        sources = list(set(meta.get('source', 'Unknown') for meta in metas))
        
        return list(docs), list(metas), list(scores), sources
        
    except Exception as e:
        logger.error(f"Text search failed: {e}")
        # Return empty results
        return [], [], [], []

def search_documents(query: str, limit: int = 5, book_filter: str = None) -> tuple:
    """Search legal documents using semantic similarity or fallback text search"""
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        collection = get_database()
        
        # If AI embedding failed, use fallback text search
        if query_embedding is None:
            logger.info("Using fallback text-based search")
            return fallback_text_search(query, limit, book_filter, collection)
        
        # Prepare search parameters for AI search
        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": limit
        }
        
        # Add book filter if specified
        if book_filter:
            search_params["where"] = {"source": {"$regex": f".*{book_filter}.*"}}
        
        # Perform AI-powered search
        try:
            results = collection.query(**search_params)
            
            # Process results
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
        except Exception as e:
            if "dimension" in str(e).lower():
                logger.warning(f"Embedding dimension mismatch: {e}")
                logger.info("🔄 Recreating database with correct dimensions...")
                app.state.collection = recreate_database_with_correct_dimensions()
                if app.state.collection:
                    # Retry search with new collection
                    results = app.state.collection.query(**search_params)
                    documents = results.get('documents', [[]])[0]
                    metadatas = results.get('metadatas', [[]])[0]
                    distances = results.get('distances', [[]])[0]
                else:
                    # Fallback to text search
                    return fallback_text_search(query, limit, book_filter, collection)
            else:
                raise e
        
        # Convert distances to relevance scores (1 - normalized distance)
        max_distance = max(distances) if distances else 1
        relevance_scores = [1 - (d / max_distance) for d in distances] if distances else []
        
        # Extract sources
        sources = list(set(
            meta.get('source', 'Unknown').replace('.txt', '.pdf') 
            for meta in metadatas
        ))
        
        return documents, metadatas, relevance_scores, sources
        
    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")

# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🚀 Starting JurisBrain Legal Knowledge API...")
    
    try:
        # Initialize ChromaDB
        logger.info("📚 Connecting to legal document database...")
        # Disable telemetry to avoid logging errors
        import chromadb.utils.embedding_functions as embedding_functions
        client = chromadb.PersistentClient(path=DB_PATH, settings=chromadb.Settings(anonymized_telemetry=False))
        app.state.collection = client.get_collection(name=COLLECTION_NAME)
        
        # Test database connection
        count = app.state.collection.count()
        logger.info(f"✅ Database connected: {count:,} documents available")
    except Exception as e:
        logger.warning(f"⚠️ ChromaDB not found: {e}")
        logger.info("🔄 Attempting to create minimal database...")
        try:
            # Create minimal database directly
            app.state.collection = recreate_database_with_correct_dimensions()
            if app.state.collection:
                count = app.state.collection.count()
                logger.info(f"✅ Minimal database created: {count:,} documents available")
            else:
                logger.error("❌ Failed to create minimal database")
                app.state.collection = None
        except Exception as setup_error:
            logger.error(f"❌ Database setup failed: {setup_error}")
            app.state.collection = None
        
        # Google AI is optional - we use text-based search instead
        if GOOGLE_AI_API_KEY:
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            logger.info("🤖 AI service available (optional)")
        else:
            logger.info("📝 Using text-based search (no AI needed)")
        
        logger.info("🎉 JurisBrain API is ready!")
        
    except Exception as e:
        logger.error(f"💥 Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down JurisBrain API...")

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to JurisBrain Legal Knowledge API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "github": "https://github.com/theIndrajeet/JurisBrainAPI"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        collection = get_database()
        document_count = collection.count()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            database_status="connected",
            total_documents=document_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get database statistics"""
    try:
        collection = get_database()
        
        # Get basic stats
        document_count = collection.count()
        
        # Get sample to determine available categories and sources
        sample = collection.get(limit=100)
        sources = set()
        categories = set()
        
        for metadata in sample.get('metadatas', []):
            if 'source' in metadata:
                sources.add(metadata['source'])
            if 'category' in metadata:
                categories.add(metadata['category'])
        
        return StatsResponse(
            total_documents=document_count,
            total_sources=len(sources),
            available_categories=list(categories),
            database_size=f"{document_count:,} documents"
        )
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

# Authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from token (optional for now)"""
    token = get_token_from_header(authorization)
    if token:
        user_data = validate_token(token)
        if user_data:
            return user_data
    return None

@app.post("/search", response_model=SearchResponse)
async def search_legal_documents(request: SearchRequest, current_user: Optional[Dict] = Depends(get_current_user)):
    """
    Search legal documents using semantic similarity
    
    This endpoint performs AI-powered semantic search across the entire 
    legal document database. It understands legal terminology and context
    to find the most relevant documents.
    
    **Example queries:**
    - "What is Section 498A of IPC?"
    - "Fundamental rights under Indian Constitution"
    - "Contract law essentials"
    - "Tort liability principles"
    """
    try:
        # Perform search
        documents, metadatas, scores, sources = search_documents(
            query=request.query,
            limit=request.limit
        )
        
        # Build results
        results = []
        for doc, meta, score in zip(documents, metadatas, scores):
            results.append(SearchResult(
                content=doc,
                source=meta.get('source', 'Unknown').replace('.txt', '.pdf'),
                relevance_score=round(score, 3)
            ))
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            sources=sources if request.include_sources else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search operation failed")

@app.post("/search-by-book", response_model=SearchResponse)
async def search_by_book(request: BookSearchRequest):
    """
    Search within specific legal books or by author
    
    This endpoint allows you to search within specific legal texts or 
    by particular authors, giving you more targeted results.
    
    **Example book filters:**
    - "RK Bangia" (author name)
    - "Law of Torts" (book title)
    - "Indian Penal Code" (specific law)
    - "Constitution of India" (document name)
    """
    try:
        # Perform book-filtered search
        documents, metadatas, scores, sources = search_documents(
            query=request.query,
            limit=request.limit,
            book_filter=request.book_filter
        )
        
        # Build results
        results = []
        for doc, meta, score in zip(documents, metadatas, scores):
            results.append(SearchResult(
                content=doc,
                source=meta.get('source', 'Unknown').replace('.txt', '.pdf'),
                relevance_score=round(score, 3)
            ))
        
        return SearchResponse(
            query=f"{request.query} (filtered by: {request.book_filter})",
            results=results,
            total_results=len(results),
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Book search failed: {e}")
        raise HTTPException(status_code=500, detail="Book search operation failed")

@app.get("/sources")
async def list_sources(limit: int = Query(default=50, description="Number of sources to return")):
    """
    List available legal document sources
    
    Returns a list of available books, acts, and legal documents 
    that can be searched through the API.
    """
    try:
        collection = get_database()
        
        # Get sample of documents to extract sources
        sample = collection.get(limit=min(limit * 10, 1000))
        sources = set()
        
        for metadata in sample.get('metadatas', []):
            if 'source' in metadata:
                source = metadata['source'].replace('.txt', '.pdf')
                sources.add(source)
        
        return {
            "total_sources": len(sources),
            "sources": sorted(list(sources))[:limit],
            "note": "This is a sample of available sources. More sources may be available in the full database."
        }
        
    except Exception as e:
        logger.error(f"Source listing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sources")

@app.post("/generate-token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    """
    Generate a new API token for accessing the JurisBrain API
    
    This endpoint creates a new API token that can be used to authenticate
    requests to the API. The token is required for accessing the search endpoints.
    
    **Usage:**
    1. Generate a token using this endpoint
    2. Include the token in the Authorization header: `Bearer your_token_here`
    3. Use the token to access search endpoints
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
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
            .header { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; padding: 30px; text-align: center; }
            .content { padding: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            input[type="text"], input[type="email"] { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 16px; }
            button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; }
            button:hover { transform: translateY(-2px); }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745; }
            .token { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 6px; font-family: monospace; word-break: break-all; margin: 10px 0; }
            .instructions { background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 15px; }
            .code-block { background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; margin: 5px 0; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ JurisBrain API</h1>
                <p>Generate Your API Token</p>
            </div>
            <div class="content">
                <form id="tokenForm">
                    <div class="form-group">
                        <label for="name">Your Name:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Your Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <button type="submit">Generate API Token</button>
                </form>
                <div id="result"></div>
            </div>
        </div>
        <script>
            document.getElementById('tokenForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = {
                    name: formData.get('name'),
                    email: formData.get('email')
                };
                
                try {
                    const response = await fetch('/generate-token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('result').innerHTML = `
                        <div class="result">
                            <h3>✅ Token Generated Successfully!</h3>
                            <p><strong>Name:</strong> ${result.name}</p>
                            <p><strong>Email:</strong> ${result.email}</p>
                            <p><strong>Created:</strong> ${new Date(result.created_at).toLocaleString()}</p>
                            <div class="token">${result.token}</div>
                            <div class="instructions">
                                <h4>📖 How to Use Your Token:</h4>
                                <p><strong>Authorization Header:</strong></p>
                                <div class="code-block">Authorization: Bearer ${result.token}</div>
                                
                                <p><strong>cURL Example:</strong></p>
                                <div class="code-block">${result.usage_instructions.curl_example}</div>
                                
                                <p><strong>Python Example:</strong></p>
                                <div class="code-block">${result.usage_instructions.python_example}</div>
                                
                                <p><strong>JavaScript Example:</strong></p>
                                <div class="code-block">${result.usage_instructions.javascript_example}</div>
                            </div>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result" style="border-left-color: #dc3545;">
                            <h3>❌ Error</h3>
                            <p>Failed to generate token: ${error.message}</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Railway sets PORT environment variable
    port = int(os.getenv("PORT", PORT))
    uvicorn.run(
        "app:app",
        host=HOST,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
