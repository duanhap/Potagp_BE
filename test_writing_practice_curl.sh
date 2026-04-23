#!/bin/bash

# ============================================
# Writing Practice API Test với CURL
# ============================================

# CONFIGURATION - Thay đổi các giá trị này
BASE_URL="http://localhost:8002/api"
FIREBASE_TOKEN="YOUR_FIREBASE_TOKEN_HERE"  # Thay bằng token thật
PATTERN_ID=1  # Thay bằng pattern_id có trong database
SENTENCE_ID=1  # Thay bằng sentence_id có trong database

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  WRITING PRACTICE API TEST SUITE${NC}"
echo -e "${BLUE}============================================${NC}\n"

# ============================================
# TEST 1: Get all unknown sentences
# ============================================
echo -e "${GREEN}TEST 1: Get Unknown Sentences${NC}"
echo -e "${YELLOW}GET ${BASE_URL}/sentences?pattern_id=${PATTERN_ID}&status=unknown${NC}\n"

curl -X GET "${BASE_URL}/sentences?pattern_id=${PATTERN_ID}&status=unknown&page=1&page_size=20" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 2: Get all known sentences
# ============================================
echo -e "${GREEN}TEST 2: Get Known Sentences${NC}"
echo -e "${YELLOW}GET ${BASE_URL}/sentences?pattern_id=${PATTERN_ID}&status=known${NC}\n"

curl -X GET "${BASE_URL}/sentences?pattern_id=${PATTERN_ID}&status=known&page=1&page_size=20" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 3: Get all sentences (no status filter)
# ============================================
echo -e "${GREEN}TEST 3: Get All Sentences (No Filter)${NC}"
echo -e "${YELLOW}GET ${BASE_URL}/sentences?pattern_id=${PATTERN_ID}${NC}\n"

curl -X GET "${BASE_URL}/sentences?pattern_id=${PATTERN_ID}&page=1&page_size=20" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 4: Get single sentence details
# ============================================
echo -e "${GREEN}TEST 4: Get Single Sentence Details${NC}"
echo -e "${YELLOW}GET ${BASE_URL}/sentences/${SENTENCE_ID}${NC}\n"

curl -X GET "${BASE_URL}/sentences/${SENTENCE_ID}" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 5: Update sentence to 'known' (Correct Answer)
# ============================================
echo -e "${GREEN}TEST 5: Update Sentence to 'known' (Correct Answer)${NC}"
echo -e "${YELLOW}PUT ${BASE_URL}/sentences/${SENTENCE_ID}${NC}\n"

curl -X PUT "${BASE_URL}/sentences/${SENTENCE_ID}" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "mistakes": 0
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 6: Update sentence mistakes (Incorrect Answer)
# ============================================
echo -e "${GREEN}TEST 6: Increment Mistakes (Incorrect Answer)${NC}"
echo -e "${YELLOW}PUT ${BASE_URL}/sentences/${SENTENCE_ID}${NC}\n"

curl -X PUT "${BASE_URL}/sentences/${SENTENCE_ID}" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "unknown",
    "mistakes": 1
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}--------------------------------------------${NC}\n"

# ============================================
# TEST 7: Create new sentence
# ============================================
echo -e "${GREEN}TEST 7: Create New Sentence${NC}"
echo -e "${YELLOW}POST ${BASE_URL}/sentences${NC}\n"

curl -X POST "${BASE_URL}/sentences" \
  -H "Authorization: Bearer ${FIREBASE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern_id": '${PATTERN_ID}',
    "term": "How are you?",
    "definition": "Bạn khỏe không?",
    "status": "unknown",
    "mistakes": 0
  }' \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo -e "\n${BLUE}============================================${NC}"
echo -e "${BLUE}  TEST SUITE COMPLETED${NC}"
echo -e "${BLUE}============================================${NC}\n"

echo -e "${YELLOW}Note: Nếu thấy lỗi 'jq: command not found', bạn có thể:${NC}"
echo -e "${YELLOW}  - Cài jq: brew install jq (Mac) hoặc apt-get install jq (Linux)${NC}"
echo -e "${YELLOW}  - Hoặc bỏ '| jq' ở cuối mỗi curl command${NC}\n"
