# CURL Commands để Test Writing Practice API

## 📝 Chuẩn bị

Trước khi chạy, thay thế các giá trị sau:
- `YOUR_FIREBASE_TOKEN` → Token Firebase thật của bạn
- `PATTERN_ID` → ID của sentence pattern có trong database (ví dụ: 1, 2, 3...)
- `SENTENCE_ID` → ID của sentence có trong database (ví dụ: 1, 2, 3...)

---

## 🔍 TEST 1: Lấy danh sách câu CHƯA THUỘC (status = unknown)

```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=unknown&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

**Mục đích:** Load tất cả câu chưa thuộc để hiển thị trong Writing Practice

**Response mong đợi:**
```json
{
  "success": true,
  "message": "Sentences retrieved successfully",
  "data": [
    {
      "id": 1,
      "term": "Where is the nearest station?",
      "definition": "Ga gần nhất ở đâu?",
      "status": "unknown",
      "number_of_mistakes": 0,
      "sentence_pattern_id": 1,
      "created_at": "2024-01-15 10:30:00",
      "last_opened": "2024-01-15 10:30:00",
      "term_language_code": "en",
      "definition_language_code": "vi"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

---

## 🔍 TEST 2: Lấy danh sách câu ĐÃ THUỘC (status = known)

```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=known&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

**Mục đích:** Kiểm tra các câu đã học xong

---

## 🔍 TEST 3: Lấy TẤT CẢ câu (không filter status)

```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

**Mục đích:** Xem tất cả câu trong pattern (cả known và unknown)

---

## 🔍 TEST 4: Lấy chi tiết 1 câu

```bash
curl -X GET "http://localhost:8002/api/sentences/1" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json"
```

**Mục đích:** Xem thông tin chi tiết của 1 câu cụ thể

---

## ✅ TEST 5: Cập nhật câu thành "ĐÃ THUỘC" (User trả lời ĐÚNG)

```bash
curl -X PUT "http://localhost:8002/api/sentences/1" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "mistakes": 0
  }'
```

**Mục đích:** Đánh dấu câu là đã thuộc khi user trả lời đúng

**Response mong đợi:**
```json
{
  "success": true,
  "message": "Sentence updated successfully",
  "data": {
    "id": 1,
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "number_of_mistakes": 0,
    ...
  }
}
```

---

## ❌ TEST 6: Tăng số lần SAI (User trả lời SAI)

```bash
curl -X PUT "http://localhost:8002/api/sentences/1" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "unknown",
    "mistakes": 1
  }'
```

**Mục đích:** Tăng counter mistakes khi user trả lời sai

**Lưu ý:** Mỗi lần sai, tăng `mistakes` lên 1

---

## ➕ TEST 7: Tạo câu mới

```bash
curl -X POST "http://localhost:8002/api/sentences" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern_id": 1,
    "term": "How are you?",
    "definition": "Bạn khỏe không?",
    "status": "unknown",
    "mistakes": 0
  }'
```

**Mục đích:** Thêm câu mới vào pattern

---

## 🔄 Luồng test hoàn chỉnh

### Bước 1: Lấy danh sách câu chưa thuộc
```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=unknown" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

### Bước 2: Giả lập user trả lời ĐÚNG → Cập nhật thành "known"
```bash
curl -X PUT "http://localhost:8002/api/sentences/1" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "mistakes": 0
  }'
```

### Bước 3: Kiểm tra lại danh sách câu chưa thuộc (câu vừa update sẽ không còn)
```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=unknown" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

### Bước 4: Kiểm tra danh sách câu đã thuộc (câu vừa update sẽ xuất hiện)
```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=known" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

---

## 🚨 Các lỗi thường gặp

### 1. 401 Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized"
}
```
**Nguyên nhân:** Firebase token không hợp lệ hoặc đã hết hạn  
**Giải pháp:** Lấy token mới từ Firebase

### 2. 404 Not Found
```json
{
  "success": false,
  "message": "Sentence pattern not found"
}
```
**Nguyên nhân:** pattern_id không tồn tại trong database  
**Giải pháp:** Kiểm tra lại pattern_id

### 3. 403 Forbidden
```json
{
  "success": false,
  "message": "You do not have permission to access this pattern"
}
```
**Nguyên nhân:** Pattern không thuộc về user này  
**Giải pháp:** Sử dụng pattern_id của chính user đang đăng nhập

### 4. 400 Bad Request
```json
{
  "success": false,
  "message": "status must be unknown or known"
}
```
**Nguyên nhân:** Giá trị status không hợp lệ  
**Giải pháp:** Chỉ dùng "unknown" hoặc "known"

---

## 💡 Tips

1. **Lấy Firebase Token:**
   - Đăng nhập vào app Android
   - Check log để lấy token
   - Hoặc dùng Firebase Console để generate token

2. **Kiểm tra pattern_id có sẵn:**
   ```bash
   curl -X GET "http://localhost:8002/api/sentence-patterns" \
     -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
   ```

3. **Format JSON đẹp hơn (nếu có jq):**
   ```bash
   curl ... | jq '.'
   ```

4. **Xem HTTP status code:**
   ```bash
   curl -w "\nHTTP Status: %{http_code}\n" ...
   ```

---

## 📱 Test trên Windows PowerShell

Nếu dùng Windows, chạy file PowerShell:
```powershell
.\test_writing_practice_curl.ps1
```

Hoặc dùng Invoke-RestMethod:
```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_FIREBASE_TOKEN"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:8002/api/sentences?pattern_id=1&status=unknown" `
    -Method Get -Headers $headers | ConvertTo-Json -Depth 10
```

---

## 🎯 Checklist Test

- [ ] Test 1: Lấy câu chưa thuộc ✅
- [ ] Test 2: Lấy câu đã thuộc ✅
- [ ] Test 3: Lấy tất cả câu ✅
- [ ] Test 4: Lấy chi tiết 1 câu ✅
- [ ] Test 5: Cập nhật thành "known" ✅
- [ ] Test 6: Tăng mistakes ✅
- [ ] Test 7: Tạo câu mới ✅

---

**Lưu ý:** Đảm bảo backend đang chạy trước khi test:
```bash
cd Potagp_BE
python run.py
```
