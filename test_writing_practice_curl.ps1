# ============================================
# Writing Practice API Test với PowerShell
# ============================================

# CONFIGURATION - Thay đổi các giá trị này
$BASE_URL = "http://localhost:8002/api"
$FIREBASE_TOKEN = "YOUR_FIREBASE_TOKEN_HERE"  # Thay bằng token thật
$PATTERN_ID = 1  # Thay bằng pattern_id có trong database
$SENTENCE_ID = 1  # Thay bằng sentence_id có trong database

$headers = @{
    "Authorization" = "Bearer $FIREBASE_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host "`n============================================" -ForegroundColor Blue
Write-Host "  WRITING PRACTICE API TEST SUITE" -ForegroundColor Blue
Write-Host "============================================`n" -ForegroundColor Blue

# ============================================
# TEST 1: Get all unknown sentences
# ============================================
Write-Host "TEST 1: Get Unknown Sentences" -ForegroundColor Green
Write-Host "GET $BASE_URL/sentences?pattern_id=$PATTERN_ID&status=unknown`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences?pattern_id=$PATTERN_ID&status=unknown&page=1&page_size=20" `
        -Method Get -Headers $headers
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 2: Get all known sentences
# ============================================
Write-Host "TEST 2: Get Known Sentences" -ForegroundColor Green
Write-Host "GET $BASE_URL/sentences?pattern_id=$PATTERN_ID&status=known`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences?pattern_id=$PATTERN_ID&status=known&page=1&page_size=20" `
        -Method Get -Headers $headers
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 3: Get all sentences (no status filter)
# ============================================
Write-Host "TEST 3: Get All Sentences (No Filter)" -ForegroundColor Green
Write-Host "GET $BASE_URL/sentences?pattern_id=$PATTERN_ID`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences?pattern_id=$PATTERN_ID&page=1&page_size=20" `
        -Method Get -Headers $headers
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 4: Get single sentence details
# ============================================
Write-Host "TEST 4: Get Single Sentence Details" -ForegroundColor Green
Write-Host "GET $BASE_URL/sentences/$SENTENCE_ID`n" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences/$SENTENCE_ID" `
        -Method Get -Headers $headers
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 5: Update sentence to 'known' (Correct Answer)
# ============================================
Write-Host "TEST 5: Update Sentence to 'known' (Correct Answer)" -ForegroundColor Green
Write-Host "PUT $BASE_URL/sentences/$SENTENCE_ID`n" -ForegroundColor Yellow

$body = @{
    term = "Where is the nearest station?"
    definition = "Ga gần nhất ở đâu?"
    status = "known"
    mistakes = 0
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences/$SENTENCE_ID" `
        -Method Put -Headers $headers -Body $body
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 6: Update sentence mistakes (Incorrect Answer)
# ============================================
Write-Host "TEST 6: Increment Mistakes (Incorrect Answer)" -ForegroundColor Green
Write-Host "PUT $BASE_URL/sentences/$SENTENCE_ID`n" -ForegroundColor Yellow

$body = @{
    term = "Where is the nearest station?"
    definition = "Ga gần nhất ở đâu?"
    status = "unknown"
    mistakes = 1
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences/$SENTENCE_ID" `
        -Method Put -Headers $headers -Body $body
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Blue

# ============================================
# TEST 7: Create new sentence
# ============================================
Write-Host "TEST 7: Create New Sentence" -ForegroundColor Green
Write-Host "POST $BASE_URL/sentences`n" -ForegroundColor Yellow

$body = @{
    pattern_id = $PATTERN_ID
    term = "How are you?"
    definition = "Bạn khỏe không?"
    status = "unknown"
    mistakes = 0
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sentences" `
        -Method Post -Headers $headers -Body $body
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n============================================" -ForegroundColor Blue
Write-Host "  TEST SUITE COMPLETED" -ForegroundColor Blue
Write-Host "============================================`n" -ForegroundColor Blue
