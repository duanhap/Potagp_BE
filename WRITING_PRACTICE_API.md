# Writing Practice API Documentation

## Tổng quan
API hỗ trợ tính năng luyện viết (Writing Practice) cho ứng dụng Potago. Người dùng sẽ xem câu tiếng Việt (definition) và viết lại bằng tiếng Anh (term).

**Base URL:** `http://localhost:8002/api`

---

## Endpoints sử dụng cho Writing Practice

### 1. Lấy danh sách câu chưa thuộc (Unknown Sentences)

Lấy tất cả các câu có status = "unknown" trong một sentence pattern để luyện viết.

**Endpoint:** `GET /sentences?pattern_id={id}&status=unknown`

**Headers:**
```
Authorization: Bearer {firebase_token}
```

**Query Parameters:**
| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `pattern_id` | `integer` | ✅ | ID của sentence pattern |
| `status` | `string` | ✅ | Giá trị: `"unknown"` hoặc `"known"` |
| `page` | `integer` | ❌ | Số trang (mặc định: 1) |
| `page_size` | `integer` | ❌ | Số câu mỗi trang (mặc định: 20) |

**Response (200 OK):**
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
            "sentence_pattern_id": 5,
            "created_at": "2024-01-15 10:30:00",
            "last_opened": "2024-01-15 10:30:00",
            "term_language_code": "en",
            "definition_language_code": "vi"
        },
        {
            "id": 2,
            "term": "How much does this cost?",
            "definition": "Cái này giá bao nhiêu?",
            "status": "unknown",
            "number_of_mistakes": 1,
            "sentence_pattern_id": 5,
            "created_at": "2024-01-15 10:31:00",
            "last_opened": "2024-01-15 10:31:00",
            "term_language_code": "en",
            "definition_language_code": "vi"
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 2,
        "total_pages": 1
    }
}
```

**Error Responses:**
- `400 Bad Request`: pattern_id không hợp lệ hoặc status không phải "unknown"/"known"
- `403 Forbidden`: Không có quyền truy cập pattern này
- `404 Not Found`: User hoặc pattern không tồn tại

---

### 2. Cập nhật trạng thái câu (Update Sentence)

Cập nhật status và số lần sai của một câu sau khi người dùng trả lời.

**Endpoint:** `PUT /sentences/{sentence_id}`

**Headers:**
```
Authorization: Bearer {firebase_token}
Content-Type: application/json
```

**Path Parameters:**
| Tham số | Kiểu | Mô tả |
|---------|------|-------|
| `sentence_id` | `integer` | ID của câu cần cập nhật |

**Request Body:**
```json
{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "mistakes": 0
}
```

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `term` | `string` | ✅ | Câu tiếng Anh (không thay đổi) |
| `definition` | `string` | ✅ | Câu tiếng Việt (không thay đổi) |
| `status` | `string` | ✅ | `"unknown"` hoặc `"known"` |
| `mistakes` | `integer` | ✅ | Số lần trả lời sai |

**Response (200 OK):**
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
        "sentence_pattern_id": 5,
        "created_at": "2024-01-15 10:30:00",
        "last_opened": "2024-01-15 10:30:00",
        "term_language_code": "en",
        "definition_language_code": "vi"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Thiếu term/definition hoặc status không hợp lệ
- `403 Forbidden`: Không có quyền cập nhật câu này
- `404 Not Found`: User, sentence hoặc pattern không tồn tại

---

## Luồng hoạt động Writing Practice

### 1. Khởi động màn hình luyện viết
```
GET /api/sentences?pattern_id=5&status=unknown&page=1&page_size=100
```
- Lấy tất cả câu chưa thuộc (status = "unknown")
- Frontend lưu danh sách này vào state
- Hiển thị câu đầu tiên

### 2. Người dùng nhập câu trả lời và nhấn "KIỂM TRA"
- Frontend so sánh câu trả lời với `term` (sau khi normalize)
- Nếu **đúng**: Hiển thị feedback màu xanh
- Nếu **sai**: Hiển thị feedback màu đỏ với đáp án đúng

### 3. Cập nhật database

#### Trường hợp trả lời ĐÚNG:
```
PUT /api/sentences/1
{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "known",
    "mistakes": 0
}
```

#### Trường hợp trả lời SAI:
```
PUT /api/sentences/1
{
    "term": "Where is the nearest station?",
    "definition": "Ga gần nhất ở đâu?",
    "status": "unknown",
    "mistakes": 1
}
```
(Tăng `mistakes` lên 1)

### 4. Chuyển sang câu tiếp theo
- Frontend tăng index lên 1
- Hiển thị câu tiếp theo trong danh sách
- Nếu hết câu: Hiển thị màn hình hoàn thành

---

## Normalize Answer Logic (Frontend)

Để so sánh câu trả lời công bằng, frontend cần normalize cả câu trả lời của user và câu đúng:

```kotlin
fun normalizeAnswer(answer: String): String {
    return answer.trim()
        .lowercase()
        .replace(Regex("[^a-z0-9\\s]"), "") // Bỏ dấu câu
        .replace(Regex("\\s+"), " ") // Normalize spaces
}

// So sánh
val isCorrect = normalizeAnswer(userAnswer) == normalizeAnswer(correctAnswer)
```

**Ví dụ:**
- User nhập: `"Where is the nearest station?"` → normalize: `"where is the nearest station"`
- Correct: `"Where is the nearest station?"` → normalize: `"where is the nearest station"`
- Kết quả: ✅ Đúng

---

## Lưu ý quan trọng

1. **Status values:**
   - `"unknown"`: Chưa thuộc (hiển thị trong luyện viết)
   - `"known"`: Đã thuộc (không hiển thị trong luyện viết)

2. **Mistakes counter:**
   - Tăng lên 1 mỗi khi trả lời sai
   - Không reset về 0 khi trả lời đúng (để tracking)

3. **Term vs Definition:**
   - `term`: Câu tiếng Anh (câu cần viết)
   - `definition`: Câu tiếng Việt (câu gợi ý)

4. **Pagination:**
   - Nên lấy tất cả câu unknown trong 1 lần (page_size lớn)
   - Hoặc implement lazy loading nếu có quá nhiều câu

5. **Authentication:**
   - Tất cả API đều yêu cầu Firebase token trong header
   - Token format: `Authorization: Bearer {firebase_token}`

---

## Test API với curl

### Test lấy danh sách câu:
```bash
curl -X GET "http://localhost:8002/api/sentences?pattern_id=1&status=unknown" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

### Test cập nhật câu:
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

---

## Kết luận

✅ **Backend đã có đầy đủ API cho Writing Practice**

Không cần thêm endpoint mới. Frontend chỉ cần:
1. Gọi GET `/api/sentences?pattern_id={id}&status=unknown` để load câu
2. Gọi PUT `/api/sentences/{id}` để cập nhật status và mistakes

Tất cả logic so sánh câu trả lời và hiển thị feedback được xử lý ở frontend.
