"""
JurisBrain Legal Knowledge API - Python Client Example

This example demonstrates how to use the JurisBrain API with Python.
It shows various ways to search legal documents and handle responses.

Requirements:
    pip install requests

Usage:
    python examples/python_example.py
"""

import requests
import json
from typing import Dict, List, Any
import time


class JurisBrainClient:
    """Python client for JurisBrain Legal Knowledge API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the JurisBrain API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Health check failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get stats: {e}")
    
    def search(self, query: str, limit: int = 5, include_sources: bool = True) -> Dict[str, Any]:
        """
        Search legal documents
        
        Args:
            query: Search query
            limit: Number of results to return (1-20)
            include_sources: Whether to include source information
            
        Returns:
            Search results dictionary
        """
        try:
            payload = {
                "query": query,
                "limit": limit,
                "include_sources": include_sources
            }
            
            response = self.session.post(
                f"{self.base_url}/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Search failed: {e}")
    
    def search_by_book(self, query: str, book_filter: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search within specific books or by author
        
        Args:
            query: Search query
            book_filter: Book name or author to filter by
            limit: Number of results to return (1-20)
            
        Returns:
            Search results dictionary
        """
        try:
            payload = {
                "query": query,
                "book_filter": book_filter,
                "limit": limit
            }
            
            response = self.session.post(
                f"{self.base_url}/search-by-book",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Book search failed: {e}")
    
    def list_sources(self, limit: int = 50) -> Dict[str, Any]:
        """
        List available legal document sources
        
        Args:
            limit: Number of sources to return
            
        Returns:
            Sources list dictionary
        """
        try:
            response = self.session.get(
                f"{self.base_url}/sources",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"Failed to list sources: {e}")


def print_search_results(results: Dict[str, Any]):
    """Pretty print search results"""
    print(f"\n🔍 Query: {results['query']}")
    print(f"📊 Found {results['total_results']} results")
    
    if results.get('sources'):
        print(f"📚 Sources: {', '.join(results['sources'][:3])}{'...' if len(results['sources']) > 3 else ''}")
    
    print("\n" + "="*80)
    
    for i, result in enumerate(results['results'], 1):
        print(f"\n{i}. 📖 Source: {result['source']}")
        print(f"   ⭐ Relevance: {result['relevance_score']:.3f}")
        print(f"   📝 Content: {result['content'][:200]}...")
        print("-" * 60)


def main():
    """Main example function"""
    # Initialize client
    client = JurisBrainClient("http://localhost:8000")
    
    print("🏛️ JurisBrain Legal Knowledge API - Python Example")
    print("=" * 60)
    
    try:
        # 1. Health Check
        print("\n1️⃣ Checking API Health...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Database: {health['database_status']}")
        print(f"   Documents: {health['total_documents']:,}")
        
        # 2. Get Statistics
        print("\n2️⃣ Getting Database Statistics...")
        stats = client.get_stats()
        print(f"   Total Documents: {stats['total_documents']:,}")
        print(f"   Total Sources: {stats['total_sources']}")
        print(f"   Categories: {', '.join(stats['available_categories'][:5])}")
        
        # 3. Basic Search Examples
        print("\n3️⃣ Basic Search Examples...")
        
        # Example 1: Constitutional Law
        results = client.search("fundamental rights under Indian Constitution", limit=3)
        print_search_results(results)
        
        # Example 2: Criminal Law
        results = client.search("Section 498A of Indian Penal Code", limit=3)
        print_search_results(results)
        
        # Example 3: Contract Law
        results = client.search("essential elements of a valid contract", limit=3)
        print_search_results(results)
        
        # 4. Book-Specific Search
        print("\n4️⃣ Book-Specific Search Example...")
        results = client.search_by_book(
            query="tort liability",
            book_filter="RK Bangia",
            limit=3
        )
        print_search_results(results)
        
        # 5. List Available Sources
        print("\n5️⃣ Available Legal Sources...")
        sources = client.list_sources(limit=10)
        print(f"📚 Total Sources: {sources['total_sources']}")
        print("   Sample Sources:")
        for source in sources['sources'][:5]:
            print(f"   • {source}")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure the JurisBrain API is running:")
        print("   docker-compose up")
        print("   or")
        print("   python app.py")


def interactive_search():
    """Interactive search mode"""
    client = JurisBrainClient("http://localhost:8000")
    
    print("\n🔍 Interactive Search Mode")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 40)
    
    while True:
        try:
            query = input("\n💬 Enter your legal question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if query.lower() == 'help':
                print("\n📖 Available commands:")
                print("   • Type any legal question to search")
                print("   • 'book:AuthorName query' for book-specific search")
                print("   • 'sources' to list available sources")
                print("   • 'stats' to show database statistics")
                print("   • 'quit' to exit")
                continue
            
            if query.lower() == 'sources':
                sources = client.list_sources(limit=20)
                print(f"\n📚 Available Sources ({sources['total_sources']} total):")
                for source in sources['sources']:
                    print(f"   • {source}")
                continue
                
            if query.lower() == 'stats':
                stats = client.get_stats()
                print(f"\n📊 Database Statistics:")
                print(f"   Documents: {stats['total_documents']:,}")
                print(f"   Sources: {stats['total_sources']}")
                print(f"   Categories: {', '.join(stats['available_categories'])}")
                continue
            
            if query.startswith('book:'):
                parts = query[5:].split(' ', 1)
                if len(parts) == 2:
                    book_filter, search_query = parts
                    results = client.search_by_book(search_query, book_filter, limit=5)
                else:
                    print("❌ Format: book:AuthorName your question")
                    continue
            else:
                results = client.search(query, limit=5)
            
            print_search_results(results)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_search()
    else:
        main()
