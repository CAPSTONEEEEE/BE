-- ----------------------------------------------------------------
-- market.sql
-- 
-- 1. 사용자 (Users) - 기본 의존성
-- 2. 상품 (Products) - ProductCreateScreen, MarketHome 기반
-- 3. 상품 이미지 (Product Images) - 1:N 관계
-- 4. 상품 문의 (Product QnA) - ProductQnAScreen 기반
-- 5. 찜 목록 (Wishlist) - MarketHome (useFavoritesStore) 기반
-- 6. AI 추천 요청 (Recommendation Requests) - 프롬프트 구조 기반
-- ----------------------------------------------------------------

-- 테이블 생성 전, 존재할 경우 삭제 (외래 키 제약 순서의 역순)
DROP TABLE IF EXISTS recommendation_requests;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS product_qna;
DROP TABLE IF EXISTS product_images;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;


-- 1. 사용자 (Users)
-- : 상품 등록(판매자), Q&A 작성(구매자), 찜하기(구매자)의 주체
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- ProductCreateScreen.js의 권한 확인 로직 기반
    is_seller BOOLEAN DEFAULT FALSE,
    business_number VARCHAR(50) UNIQUE, -- 사업자 등록번호
    seller_status VARCHAR(20) DEFAULT 'pending', -- (예: 'pending', 'approved', 'rejected')
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 2. 상품 (Products)
-- : ProductCreateScreen.js (입력), MarketHome.js (출력) 기반
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id), -- 판매자 ID
    
    -- ProductCreateScreen.js 폼 필드
    title VARCHAR(255) NOT NULL,
    price INT NOT NULL DEFAULT 0,
    shop_name VARCHAR(100),
    location VARCHAR(255),
    summary TEXT,
    seller_note TEXT,
    delivery_info VARCHAR(255),
    
    -- MarketHome.js 필터링/정렬 필드
    region VARCHAR(50),
    rating DECIMAL(3, 2) DEFAULT 0.00,
    likes INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 3. 상품 이미지 (Product Images)
-- : ProductCreateScreen.js의 다중 이미지 업로드 지원
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url VARCHAR(1024) NOT NULL,
    is_thumbnail BOOLEAN DEFAULT FALSE, -- MarketHome.js 목록 썸네일용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 4. 상품 문의 (Product QnA)
-- : ProductQnAScreen.js 기반
CREATE TABLE product_qna (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    author_id INT NOT NULL REFERENCES users(id), -- 질문자 User ID
    
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    
    -- 판매자 답변용 (Nullable)
    answer_body TEXT,
    answered_by_id INT REFERENCES users(id), -- 답변자(판매자) User ID
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP -- 답변이 달린 시간
);


-- 5. 찜 목록 (Wishlist / Product Likes)
-- : MarketHome.js의 useFavoritesStore, isFavorite 로직 지원
CREATE TABLE wishlist (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 한 유저가 한 상품에 '좋아요'는 한 번만 가능
    UNIQUE(user_id, product_id)
);


-- 6. AI 추천 요청 (Recommendation Requests)
-- : 제공해주신 '추천 프롬프트' 구조 기반
CREATE TABLE recommendation_requests (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id), -- 비회원도 요청 가능하도록 Nullable
    
    -- [요구사항]
    age VARCHAR(50),
    relation VARCHAR(100),
    people INT,
    period VARCHAR(100),
    "when" VARCHAR(100), -- "when"은 SQL 예약어일 수 있으므로 따옴표 처리
    transportation VARCHAR(100),
    style TEXT,
    budget VARCHAR(100),
    etc TEXT,
    
    -- [생성 규칙]
    recommend_count INT,
    
    -- [AI 응답]
    response_json JSONB, -- AI가 생성한 JSON 결과를 저장 (JSONB가 검색에 유리)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 추가 (성능 향상을 위해)
CREATE INDEX idx_products_region ON products(region);
CREATE INDEX idx_products_likes ON products(likes DESC);
CREATE INDEX idx_products_rating ON products(rating DESC);
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_product_qna_product_id ON product_qna(product_id);
CREATE INDEX idx_wishlist_user_id ON wishlist(user_id);