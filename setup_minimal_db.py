#!/usr/bin/env python3
"""
Setup script to create a minimal database for Render deployment
This creates a small sample database for testing purposes
"""

import os
import chromadb
from chromadb.config import Settings
import json

def create_minimal_database():
    """Create a minimal legal database for testing"""
    
    # Create database directory
    db_path = "legal_db"
    os.makedirs(db_path, exist_ok=True)
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=db_path)
    
    # Create collection
    collection = client.get_or_create_collection(
        name="law_books",
        metadata={"description": "Minimal legal database for testing"}
    )
    
    # Sample legal documents for testing
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
    
    print(f"✅ Created minimal database with {len(sample_documents)} sample documents")
    print(f"📁 Database location: {os.path.abspath(db_path)}")
    
    # Print collection info
    count = collection.count()
    print(f"📊 Total documents in collection: {count}")
    
    return True

if __name__ == "__main__":
    print("🏗️ Setting up minimal legal database for Render deployment...")
    create_minimal_database()
    print("✅ Database setup complete!")
