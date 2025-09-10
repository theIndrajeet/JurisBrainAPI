#!/bin/bash

# JurisBrain Legal Knowledge API - cURL Examples
# 
# This script demonstrates how to use the JurisBrain API with cURL commands.
# Perfect for testing, scripting, and integration with shell scripts.
#
# Usage:
#   chmod +x examples/curl_examples.sh
#   ./examples/curl_examples.sh
#
# Or run individual commands by copying them from this file.

# =============================================================================
# Configuration
# =============================================================================

# API Base URL (change if running on different host/port)
API_URL="http://localhost:8000"

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored headers
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "$(printf '=%.0s' {1..60})"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}💡 $1${NC}"
}

# Function to check if API is running
check_api() {
    if ! curl -s "$API_URL/health" > /dev/null; then
        print_error "API is not running at $API_URL"
        print_info "Start the API with: docker-compose up or python app.py"
        exit 1
    fi
}

# =============================================================================
# Example Functions
# =============================================================================

# 1. Health Check
health_check() {
    print_header "1️⃣ Health Check"
    
    echo "Command:"
    echo "curl -X GET '$API_URL/health'"
    echo ""
    
    response=$(curl -s -X GET "$API_URL/health")
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "healthy"; then
        print_success "API is healthy!"
    else
        print_error "API health check failed"
    fi
}

# 2. Database Statistics
get_stats() {
    print_header "2️⃣ Database Statistics"
    
    echo "Command:"
    echo "curl -X GET '$API_URL/stats'"
    echo ""
    
    response=$(curl -s -X GET "$API_URL/stats")
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
}

# 3. Basic Search Examples
basic_search() {
    print_header "3️⃣ Basic Legal Document Search"
    
    # Example 1: Constitutional Law
    echo "🔍 Example 1: Searching for 'fundamental rights under Indian Constitution'"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"fundamental rights under Indian Constitution\", \"limit\": 3}'"
    echo ""
    
    response=$(curl -s -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "fundamental rights under Indian Constitution", "limit": 3}')
    
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    
    # Example 2: Criminal Law
    echo "🔍 Example 2: Searching for 'Section 498A of Indian Penal Code'"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"Section 498A of Indian Penal Code\", \"limit\": 2}'"
    echo ""
    
    response=$(curl -s -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "Section 498A of Indian Penal Code", "limit": 2}')
    
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
}

# 4. Book-Specific Search
book_search() {
    print_header "4️⃣ Book-Specific Search"
    
    echo "🔍 Searching for 'tort liability' in books by 'RK Bangia'"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search-by-book' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"tort liability\", \"book_filter\": \"RK Bangia\", \"limit\": 3}'"
    echo ""
    
    response=$(curl -s -X POST "$API_URL/search-by-book" \
        -H "Content-Type: application/json" \
        -d '{"query": "tort liability", "book_filter": "RK Bangia", "limit": 3}')
    
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
}

# 5. List Sources
list_sources() {
    print_header "5️⃣ List Available Sources"
    
    echo "Command:"
    echo "curl -X GET '$API_URL/sources?limit=10'"
    echo ""
    
    response=$(curl -s -X GET "$API_URL/sources?limit=10")
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
}

# 6. Error Handling Examples
error_examples() {
    print_header "6️⃣ Error Handling Examples"
    
    # Example 1: Empty query
    echo "❌ Example 1: Empty query (should return 422 error)"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"\", \"limit\": 5}'"
    echo ""
    
    response=$(curl -s -w "HTTP Status: %{http_code}\n" -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "", "limit": 5}')
    
    echo "Response:"
    echo "$response"
    echo ""
    
    # Example 2: Invalid limit
    echo "❌ Example 2: Invalid limit (should return 422 error)"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"test\", \"limit\": 25}'"
    echo ""
    
    response=$(curl -s -w "HTTP Status: %{http_code}\n" -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "test", "limit": 25}')
    
    echo "Response:"
    echo "$response"
}

# 7. Advanced Examples
advanced_examples() {
    print_header "7️⃣ Advanced Usage Examples"
    
    # Example 1: Search with custom headers
    echo "🔧 Example 1: Search with custom headers and verbose output"
    echo ""
    echo "Command:"
    echo "curl -v -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -H 'User-Agent: MyLegalApp/1.0' \\"
    echo "  -d '{\"query\": \"contract law essentials\", \"limit\": 2, \"include_sources\": false}'"
    echo ""
    
    response=$(curl -s -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -H "User-Agent: MyLegalApp/1.0" \
        -d '{"query": "contract law essentials", "limit": 2, "include_sources": false}')
    
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    
    # Example 2: Save response to file
    echo "💾 Example 2: Save search results to file"
    echo ""
    echo "Command:"
    echo "curl -X POST '$API_URL/search' \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"property law basics\", \"limit\": 5}' \\"
    echo "  -o search_results.json"
    echo ""
    
    curl -s -X POST "$API_URL/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "property law basics", "limit": 5}' \
        -o search_results.json
    
    if [ -f "search_results.json" ]; then
        print_success "Results saved to search_results.json"
        echo "File size: $(wc -c < search_results.json) bytes"
        echo "Preview:"
        head -n 10 search_results.json
    else
        print_error "Failed to save results"
    fi
}

# 8. Batch Processing Example
batch_processing() {
    print_header "8️⃣ Batch Processing Example"
    
    echo "📋 Processing multiple queries in sequence"
    echo ""
    
    # Array of queries
    queries=(
        "What is a tort?"
        "Essential elements of contract"
        "Fundamental rights in Constitution"
        "Criminal procedure code basics"
    )
    
    for i in "${!queries[@]}"; do
        echo "Query $((i+1)): ${queries[i]}"
        
        response=$(curl -s -X POST "$API_URL/search" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"${queries[i]}\", \"limit\": 1}")
        
        # Extract just the result count
        result_count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_results'])" 2>/dev/null || echo "0")
        
        echo "  → Found $result_count results"
        echo ""
        
        # Small delay to be respectful to the API
        sleep 0.5
    done
}

# =============================================================================
# Interactive Mode
# =============================================================================

interactive_mode() {
    print_header "🔍 Interactive Search Mode"
    print_info "Enter your legal questions (type 'quit' to exit)"
    
    while true; do
        echo -n "💬 Legal question: "
        read -r query
        
        case "$query" in
            "quit"|"exit"|"q")
                echo "👋 Goodbye!"
                break
                ;;
            "help")
                echo ""
                echo "Available commands:"
                echo "  • Type any legal question to search"
                echo "  • 'stats' - Show database statistics"
                echo "  • 'sources' - List available sources"
                echo "  • 'help' - Show this help"
                echo "  • 'quit' - Exit interactive mode"
                echo ""
                ;;
            "stats")
                response=$(curl -s -X GET "$API_URL/stats")
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
                echo ""
                ;;
            "sources")
                response=$(curl -s -X GET "$API_URL/sources?limit=10")
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
                echo ""
                ;;
            "")
                echo "Please enter a question or command"
                ;;
            *)
                echo "🔍 Searching for: $query"
                response=$(curl -s -X POST "$API_URL/search" \
                    -H "Content-Type: application/json" \
                    -d "{\"query\": \"$query\", \"limit\": 3}")
                
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
                echo ""
                ;;
        esac
    done
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    echo -e "${BLUE}🏛️ JurisBrain Legal Knowledge API - cURL Examples${NC}"
    echo "$(printf '=%.0s' {1..60})"
    
    # Check if API is running
    check_api
    
    # Show menu if no arguments provided
    if [ $# -eq 0 ]; then
        echo ""
        echo "Choose an option:"
        echo "1. Run all examples"
        echo "2. Health check only"
        echo "3. Basic search examples"
        echo "4. Interactive search mode"
        echo "5. Advanced examples"
        echo ""
        echo -n "Enter choice (1-5): "
        read -r choice
        
        case $choice in
            1)
                health_check
                get_stats
                basic_search
                book_search
                list_sources
                error_examples
                advanced_examples
                batch_processing
                ;;
            2)
                health_check
                ;;
            3)
                basic_search
                ;;
            4)
                interactive_mode
                ;;
            5)
                advanced_examples
                ;;
            *)
                echo "Invalid choice"
                exit 1
                ;;
        esac
    else
        # Handle command line arguments
        case $1 in
            "health")
                health_check
                ;;
            "stats")
                get_stats
                ;;
            "search")
                basic_search
                ;;
            "book")
                book_search
                ;;
            "sources")
                list_sources
                ;;
            "errors")
                error_examples
                ;;
            "advanced")
                advanced_examples
                ;;
            "batch")
                batch_processing
                ;;
            "interactive")
                interactive_mode
                ;;
            "all")
                health_check
                get_stats
                basic_search
                book_search
                list_sources
                error_examples
                advanced_examples
                batch_processing
                ;;
            *)
                echo "Usage: $0 [health|stats|search|book|sources|errors|advanced|batch|interactive|all]"
                exit 1
                ;;
        esac
    fi
    
    print_success "Examples completed!"
}

# Run main function with all arguments
main "$@"
