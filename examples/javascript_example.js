/**
 * JurisBrain Legal Knowledge API - JavaScript Client Example
 * 
 * This example demonstrates how to use the JurisBrain API with JavaScript.
 * Works in both Node.js and browser environments.
 * 
 * For Node.js:
 *   npm install axios
 *   node examples/javascript_example.js
 * 
 * For Browser:
 *   Include this script in your HTML page
 */

// Use axios for Node.js or fetch for browser
const isNode = typeof window === 'undefined';
let httpClient;

if (isNode) {
    // Node.js environment
    const axios = require('axios');
    httpClient = axios;
} else {
    // Browser environment - use fetch API
    httpClient = {
        get: async (url, config = {}) => {
            const response = await fetch(url, {
                method: 'GET',
                headers: config.headers || {}
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return { data: await response.json() };
        },
        post: async (url, data, config = {}) => {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...config.headers
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return { data: await response.json() };
        }
    };
}

/**
 * JurisBrain API Client Class
 */
class JurisBrainClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    /**
     * Check API health status
     */
    async healthCheck() {
        try {
            const response = await httpClient.get(`${this.baseUrl}/health`);
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }

    /**
     * Get database statistics
     */
    async getStats() {
        try {
            const response = await httpClient.get(`${this.baseUrl}/stats`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get stats: ${error.message}`);
        }
    }

    /**
     * Search legal documents
     */
    async search(query, options = {}) {
        const { limit = 5, includeSources = true } = options;
        
        try {
            const payload = {
                query,
                limit,
                include_sources: includeSources
            };

            const response = await httpClient.post(`${this.baseUrl}/search`, payload);
            return response.data;
        } catch (error) {
            throw new Error(`Search failed: ${error.message}`);
        }
    }

    /**
     * Search within specific books or by author
     */
    async searchByBook(query, bookFilter, options = {}) {
        const { limit = 5 } = options;
        
        try {
            const payload = {
                query,
                book_filter: bookFilter,
                limit
            };

            const response = await httpClient.post(`${this.baseUrl}/search-by-book`, payload);
            return response.data;
        } catch (error) {
            throw new Error(`Book search failed: ${error.message}`);
        }
    }

    /**
     * List available legal document sources
     */
    async listSources(limit = 50) {
        try {
            const response = await httpClient.get(`${this.baseUrl}/sources?limit=${limit}`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to list sources: ${error.message}`);
        }
    }
}

/**
 * Utility function to format search results
 */
function formatSearchResults(results) {
    console.log(`\n🔍 Query: ${results.query}`);
    console.log(`📊 Found ${results.total_results} results`);
    
    if (results.sources && results.sources.length > 0) {
        const sourcesDisplay = results.sources.slice(0, 3).join(', ');
        const moreText = results.sources.length > 3 ? '...' : '';
        console.log(`📚 Sources: ${sourcesDisplay}${moreText}`);
    }
    
    console.log('\n' + '='.repeat(80));
    
    results.results.forEach((result, index) => {
        console.log(`\n${index + 1}. 📖 Source: ${result.source}`);
        console.log(`   ⭐ Relevance: ${result.relevance_score.toFixed(3)}`);
        console.log(`   📝 Content: ${result.content.substring(0, 200)}...`);
        console.log('-'.repeat(60));
    });
}

/**
 * Main example function
 */
async function runExamples() {
    const client = new JurisBrainClient('http://localhost:8000');
    
    console.log('🏛️ JurisBrain Legal Knowledge API - JavaScript Example');
    console.log('='.repeat(60));
    
    try {
        // 1. Health Check
        console.log('\n1️⃣ Checking API Health...');
        const health = await client.healthCheck();
        console.log(`   Status: ${health.status}`);
        console.log(`   Database: ${health.database_status}`);
        console.log(`   Documents: ${health.total_documents.toLocaleString()}`);
        
        // 2. Get Statistics
        console.log('\n2️⃣ Getting Database Statistics...');
        const stats = await client.getStats();
        console.log(`   Total Documents: ${stats.total_documents.toLocaleString()}`);
        console.log(`   Total Sources: ${stats.total_sources}`);
        console.log(`   Categories: ${stats.available_categories.slice(0, 5).join(', ')}`);
        
        // 3. Basic Search Examples
        console.log('\n3️⃣ Basic Search Examples...');
        
        // Example 1: Constitutional Law
        let results = await client.search('fundamental rights under Indian Constitution', { limit: 3 });
        formatSearchResults(results);
        
        // Example 2: Criminal Law
        results = await client.search('Section 498A of Indian Penal Code', { limit: 3 });
        formatSearchResults(results);
        
        // Example 3: Contract Law
        results = await client.search('essential elements of a valid contract', { limit: 3 });
        formatSearchResults(results);
        
        // 4. Book-Specific Search
        console.log('\n4️⃣ Book-Specific Search Example...');
        results = await client.searchByBook('tort liability', 'RK Bangia', { limit: 3 });
        formatSearchResults(results);
        
        // 5. List Available Sources
        console.log('\n5️⃣ Available Legal Sources...');
        const sources = await client.listSources(10);
        console.log(`📚 Total Sources: ${sources.total_sources}`);
        console.log('   Sample Sources:');
        sources.sources.slice(0, 5).forEach(source => {
            console.log(`   • ${source}`);
        });
        
        console.log('\n✅ All examples completed successfully!');
        
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        console.log('\n💡 Make sure the JurisBrain API is running:');
        console.log('   docker-compose up');
        console.log('   or');
        console.log('   python app.py');
    }
}

/**
 * Browser-specific interactive search
 */
function createInteractiveSearch() {
    if (typeof window === 'undefined') return; // Only for browser
    
    const client = new JurisBrainClient('http://localhost:8000');
    
    // Create UI elements
    const container = document.createElement('div');
    container.innerHTML = `
        <div style="max-width: 800px; margin: 20px auto; padding: 20px; font-family: Arial, sans-serif;">
            <h1>🏛️ JurisBrain Legal Search</h1>
            <div style="margin-bottom: 20px;">
                <input type="text" id="searchInput" placeholder="Enter your legal question..." 
                       style="width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px;">
                <button id="searchBtn" style="padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Search</button>
            </div>
            <div style="margin-bottom: 20px;">
                <label>
                    <input type="checkbox" id="bookSearch"> Search in specific book/author:
                    <input type="text" id="bookFilter" placeholder="e.g., RK Bangia" style="margin-left: 10px; padding: 5px;">
                </label>
            </div>
            <div id="results" style="margin-top: 20px;"></div>
        </div>
    `;
    
    document.body.appendChild(container);
    
    // Add event listeners
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    
    async function performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const bookSearch = document.getElementById('bookSearch').checked;
        const bookFilter = document.getElementById('bookFilter').value.trim();
        const resultsDiv = document.getElementById('results');
        
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        resultsDiv.innerHTML = '<div>🔍 Searching...</div>';
        
        try {
            let results;
            if (bookSearch && bookFilter) {
                results = await client.searchByBook(query, bookFilter, { limit: 5 });
            } else {
                results = await client.search(query, { limit: 5 });
            }
            
            // Display results
            let html = `<h3>Results for: "${results.query}"</h3>`;
            html += `<p>Found ${results.total_results} results</p>`;
            
            if (results.sources && results.sources.length > 0) {
                html += `<p><strong>Sources:</strong> ${results.sources.join(', ')}</p>`;
            }
            
            results.results.forEach((result, index) => {
                html += `
                    <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px;">
                        <h4>${index + 1}. ${result.source}</h4>
                        <p><strong>Relevance:</strong> ${result.relevance_score.toFixed(3)}</p>
                        <p>${result.content}</p>
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
            
        } catch (error) {
            resultsDiv.innerHTML = `<div style="color: red;">❌ Error: ${error.message}</div>`;
        }
    }
}

// Export for Node.js or run examples
if (isNode) {
    // Node.js environment
    if (require.main === module) {
        runExamples().catch(console.error);
    }
    module.exports = { JurisBrainClient, runExamples };
} else {
    // Browser environment
    window.JurisBrainClient = JurisBrainClient;
    window.runJurisBrainExamples = runExamples;
    window.createJurisBrainSearch = createInteractiveSearch;
    
    // Auto-create interactive search if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createInteractiveSearch);
    } else {
        createInteractiveSearch();
    }
}
