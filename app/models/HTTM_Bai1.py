import numpy as np
import faiss

N, D = 1_000_000, 128
X = np.random.rand(N, D).astype('float32')
q = np.random.rand(1, D).astype('float32')  # faiss cần shape (1, D)
K = 5

# Build index 
index = faiss.IndexFlatIP(D)  # dùng cosine nếu normalize trước

# Normalize để dùng cosine similarity
faiss.normalize_L2(X)
faiss.normalize_L2(q)

# Add data
index.add(X)

# Search
scores, indices = index.search(q, K)

print("Top-K indices:", indices[0])
print("Top-K scores:", scores[0])
