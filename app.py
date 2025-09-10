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
from typing import List, Dict, Any, Optional
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Model configurations
EMBEDDING_MODEL = "models/embedding-001"
TASK_TYPE = "retrieval_query"

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

def get_embedding_client():
    """Get Google AI embedding client"""
    if not GOOGLE_AI_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")
    return genai

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using Google AI"""
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type=TASK_TYPE
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

def search_documents(query: str, limit: int = 5, book_filter: str = None) -> tuple:
    """Search legal documents using semantic similarity"""
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Prepare search parameters
        search_params = {
            "query_embeddings": [query_embedding],
            "n_results": limit
        }
        
        # Add book filter if specified
        if book_filter:
            search_params["where"] = {"source": {"$regex": f".*{book_filter}.*"}}
        
        # Perform search
        collection = get_database()
        results = collection.query(**search_params)
        
        # Process results
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
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
        client = chromadb.PersistentClient(path=DB_PATH)
        app.state.collection = client.get_collection(name=COLLECTION_NAME)
        
        # Test database connection
        count = app.state.collection.count()
        logger.info(f"✅ Database connected: {count:,} documents available")
        
        # Initialize Google AI (if API key provided)
        if GOOGLE_AI_API_KEY:
            genai.configure(api_key=GOOGLE_AI_API_KEY)
            logger.info("🤖 AI embedding service configured")
        else:
            logger.warning("⚠️  Google AI API key not provided - some features may be limited")
        
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

@app.post("/search", response_model=SearchResponse)
async def search_legal_documents(request: SearchRequest):
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
