#!/usr/bin/env python3
"""
JurisBrain Legal Knowledge API Client
A simple Python client for the JurisBrain Legal Knowledge API
"""

import requests
import json
from typing import List, Dict, Optional, Union


class JurisBrainClient:
    """
    Client for the JurisBrain Legal Knowledge API
    
    This client provides easy access to the JurisBrain Legal Knowledge API,
    allowing you to search through legal documents, get statistics, and
    retrieve available sources.
    """
    
    def __init__(self, base_url: str = "https://jurisbrainapi.onrender.com"):
        """
        Initialize the JurisBrain client
        
        Args:
            base_url: The base URL of the JurisBrain API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'JurisBrain-Python-Client/1.0'
        })
    
    def search(self, query: str, limit: int = 5, book_filter: Optional[str] = None) -> Dict:
        """
        Search for legal documents
        
        Args:
            query: The search query
            limit: Maximum number of results to return (default: 5)
            book_filter: Optional filter to search within a specific book
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = JurisBrainClient()
            >>> results = client.search("fundamental rights", limit=3)
            >>> print(f"Found {results['total_results']} results")
        """
        payload = {
            "query": query,
            "limit": limit
        }
        
        if book_filter:
            payload["book_filter"] = book_filter
        
        try:
            response = self.session.post(f"{self.base_url}/search", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Search failed: {str(e)}",
                "query": query,
                "results": [],
                "total_results": 0,
                "sources": []
            }
    
    def get_sources(self) -> Dict:
        """
        Get all available legal sources
        
        Returns:
            Dictionary containing available sources
            
        Example:
            >>> client = JurisBrainClient()
            >>> sources = client.get_sources()
            >>> print(f"Available sources: {sources['total_sources']}")
        """
        try:
            response = self.session.get(f"{self.base_url}/sources")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to retrieve sources: {str(e)}",
                "sources": [],
                "total_sources": 0
            }
    
    def get_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary containing database statistics
            
        Example:
            >>> client = JurisBrainClient()
            >>> stats = client.get_stats()
            >>> print(f"Total documents: {stats['total_documents']}")
        """
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to retrieve statistics: {str(e)}",
                "total_documents": 0,
                "total_sources": 0,
                "categories": []
            }
    
    def health_check(self) -> Dict:
        """
        Check if the API is healthy
        
        Returns:
            Dictionary containing health status
            
        Example:
            >>> client = JurisBrainClient()
            >>> health = client.health_check()
            >>> print(f"API Status: {health.get('status', 'unknown')}")
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Health check failed: {str(e)}",
                "status": "unhealthy"
            }
    
    def search_by_category(self, query: str, category: str, limit: int = 5) -> Dict:
        """
        Search for documents within a specific legal category
        
        Args:
            query: The search query
            category: The legal category to search in
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = JurisBrainClient()
            >>> results = client.search_by_category("rights", "Constitutional Law")
        """
        # First get all sources to find books in the category
        sources = self.get_sources()
        if "error" in sources:
            return sources
        
        # Find books in the specified category
        category_books = []
        for source in sources.get("sources", []):
            if source.get("category", "").lower() == category.lower():
                category_books.append(source.get("source", ""))
        
        if not category_books:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "sources": [],
                "message": f"No books found in category: {category}"
            }
        
        # Search in each book
        all_results = []
        all_sources = set()
        
        for book in category_books:
            result = self.search(query, limit=limit, book_filter=book)
            if "error" not in result:
                all_results.extend(result.get("results", []))
                all_sources.update(result.get("sources", []))
        
        # Sort by score and limit results
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        all_results = all_results[:limit]
        
        return {
            "query": query,
            "results": all_results,
            "total_results": len(all_results),
            "sources": list(all_sources)
        }


def main():
    """
    Example usage of the JurisBrain client
    """
    print("🏛️ JurisBrain Legal Knowledge API Client Demo")
    print("=" * 50)
    
    # Initialize client
    client = JurisBrainClient()
    
    # Health check
    print("\n🔍 Checking API health...")
    health = client.health_check()
    if "error" in health:
        print(f"❌ API is not healthy: {health['error']}")
        return
    else:
        print("✅ API is healthy")
    
    # Get statistics
    print("\n📊 Getting database statistics...")
    stats = client.get_stats()
    if "error" not in stats:
        print(f"📚 Total documents: {stats.get('total_documents', 'Unknown')}")
        print(f"📖 Total sources: {stats.get('total_sources', 'Unknown')}")
        print(f"🏷️ Categories: {', '.join(stats.get('categories', []))}")
    else:
        print(f"❌ Failed to get stats: {stats['error']}")
    
    # Search examples
    search_queries = [
        "fundamental rights",
        "constitution",
        "contract law",
        "tort liability"
    ]
    
    print("\n🔍 Testing search functionality...")
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        results = client.search(query, limit=2)
        
        if "error" in results:
            print(f"❌ Search failed: {results['error']}")
        else:
            print(f"✅ Found {results['total_results']} results")
            for i, result in enumerate(results['results'][:2], 1):
                print(f"  {i}. {result['metadata']['book']} (Score: {result['score']:.1f})")
                print(f"     {result['content'][:100]}...")
    
    # Category search example
    print(f"\n🏷️ Searching in Constitutional Law category...")
    category_results = client.search_by_category("rights", "Constitutional Law", limit=2)
    if "error" not in category_results:
        print(f"✅ Found {category_results['total_results']} results in Constitutional Law")
        for result in category_results['results']:
            print(f"  - {result['metadata']['book']} (Score: {result['score']:.1f})")
    else:
        print(f"❌ Category search failed: {category_results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
