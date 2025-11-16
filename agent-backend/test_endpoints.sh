#!/bin/bash
# Comprehensive test script for agent-backend endpoints
# Usage: ./test_endpoints.sh
# Requirements: curl, jq (optional, for pretty JSON)

BASE_URL="http://localhost:5000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Testing Agent Backend API"
echo "=========================================="
echo ""

# Check if server is running
echo "Checking if server is running..."
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
  echo -e "${RED}❌ Server is not running!${NC}"
  echo "Please start the server with: python app.py"
  exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test 1: Health Check
echo "1. Testing /health endpoint..."
HEALTH=$(curl -s "$BASE_URL/health")
if command -v jq &> /dev/null; then
  echo "$HEALTH" | jq .
else
  echo "$HEALTH"
fi
echo ""

# Test 2: Index
echo "2. Testing / endpoint..."
INDEX=$(curl -s "$BASE_URL/")
if command -v jq &> /dev/null; then
  echo "$INDEX" | jq .
else
  echo "$INDEX"
fi
echo ""

# Test 3: Plan
echo "3. Testing /api/plan endpoint..."
PLAN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/plan" \
  -H "Content-Type: application/json" \
  -d '{"task": "Plan a 3-day trip to Tokyo"}')

if command -v jq &> /dev/null; then
  echo "$PLAN_RESPONSE" | jq .
  THREAD_ID=$(echo "$PLAN_RESPONSE" | jq -r '.thread_id')
  PLAN=$(echo "$PLAN_RESPONSE" | jq -r '.plan')
else
  echo "$PLAN_RESPONSE"
  # Basic extraction without jq (fallback)
  THREAD_ID=$(echo "$PLAN_RESPONSE" | grep -o '"thread_id":[0-9]*' | cut -d':' -f2)
  PLAN=$(echo "$PLAN_RESPONSE" | grep -o '"plan":"[^"]*' | cut -d'"' -f4)
fi

if [ -n "$THREAD_ID" ] && [ "$THREAD_ID" != "null" ]; then
  echo -e "${GREEN}✅ Plan created successfully${NC}"
  echo "Thread ID: $THREAD_ID"
  echo "Plan length: ${#PLAN} characters"
else
  echo -e "${RED}❌ Plan creation failed${NC}"
  exit 1
fi
echo ""

# Test 4: Research
if [ -n "$THREAD_ID" ] && [ -n "$PLAN" ]; then
  echo "4. Testing /api/research endpoint..."
  # Escape plan for JSON
  PLAN_ESCAPED=$(echo "$PLAN" | sed 's/"/\\"/g')
  RESEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/research" \
    -H "Content-Type: application/json" \
    -d "{\"plan\": \"$PLAN_ESCAPED\", \"thread_id\": $THREAD_ID}")
  
  if command -v jq &> /dev/null; then
    echo "$RESEARCH_RESPONSE" | jq .
    QUERIES_COUNT=$(echo "$RESEARCH_RESPONSE" | jq '.queries | length')
    ANSWERS_COUNT=$(echo "$RESEARCH_RESPONSE" | jq '.answers | length')
    echo "Queries: $QUERIES_COUNT, Answers: $ANSWERS_COUNT"
  else
    echo "$RESEARCH_RESPONSE"
  fi
  echo ""
fi

# Test 5: Generate
if [ -n "$THREAD_ID" ] && [ -n "$PLAN" ]; then
  echo "5. Testing /api/generate endpoint..."
  PLAN_ESCAPED=$(echo "$PLAN" | sed 's/"/\\"/g')
  GENERATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/generate" \
    -H "Content-Type: application/json" \
    -d "{\"task\": \"Plan a 3-day trip to Tokyo\", \"plan\": \"$PLAN_ESCAPED\", \"thread_id\": $THREAD_ID}")
  
  if command -v jq &> /dev/null; then
    echo "$GENERATE_RESPONSE" | jq '.draft' | head -c 200
    echo "..."
    DRAFT=$(echo "$GENERATE_RESPONSE" | jq -r '.draft')
  else
    echo "$GENERATE_RESPONSE" | head -c 200
    echo "..."
  fi
  echo ""
fi

# Test 6: Critique
if [ -n "$THREAD_ID" ] && [ -n "$DRAFT" ]; then
  echo "6. Testing /api/critique endpoint..."
  DRAFT_ESCAPED=$(echo "$DRAFT" | sed 's/"/\\"/g')
  CRITIQUE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/critique" \
    -H "Content-Type: application/json" \
    -d "{\"draft\": \"$DRAFT_ESCAPED\", \"thread_id\": $THREAD_ID}")
  
  if command -v jq &> /dev/null; then
    echo "$CRITIQUE_RESPONSE" | jq '.critique' | head -c 200
    echo "..."
  else
    echo "$CRITIQUE_RESPONSE" | head -c 200
    echo "..."
  fi
  echo ""
fi

# Test 7: Get State
if [ -n "$THREAD_ID" ]; then
  echo "7. Testing /api/get-state endpoint..."
  STATE_RESPONSE=$(curl -s "$BASE_URL/api/get-state?thread_id=$THREAD_ID")
  if command -v jq &> /dev/null; then
    echo "$STATE_RESPONSE" | jq '.values | keys'
  else
    echo "$STATE_RESPONSE"
  fi
  echo ""
fi

# Test 8: Error handling - missing task
echo "8. Testing error handling (missing task)..."
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/plan" \
  -H "Content-Type: application/json" \
  -d '{}')
if command -v jq &> /dev/null; then
  echo "$ERROR_RESPONSE" | jq .
else
  echo "$ERROR_RESPONSE"
fi
if echo "$ERROR_RESPONSE" | grep -q "error"; then
  echo -e "${GREEN}✅ Error handling works correctly${NC}"
else
  echo -e "${YELLOW}⚠️  Expected error response${NC}"
fi
echo ""

# Test 9: Error handling - missing plan in research
echo "9. Testing error handling (missing plan in research)..."
ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/research" \
  -H "Content-Type: application/json" \
  -d "{\"thread_id\": $THREAD_ID}")
if command -v jq &> /dev/null; then
  echo "$ERROR_RESPONSE" | jq .
else
  echo "$ERROR_RESPONSE"
fi
if echo "$ERROR_RESPONSE" | grep -q "error"; then
  echo -e "${GREEN}✅ Error handling works correctly${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Tests complete!${NC}"
echo "=========================================="

