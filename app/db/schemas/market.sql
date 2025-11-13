-- ----------------------------------------------------------------
-- market.sql (MySQL Version for sosohaeng_db)
--
-- 테이블명 변경:
-- 1. users -> market_users
-- 2. products -> market_products
-- 3. product_qna -> market_qna
-- 4. (일관성) product_images -> market_product_images
-- 5. (일관성) wishlist -> market_wishlist
-- 6. (일관성) recommendation_requests -> market_recommendation_requests
-- ----------------------------------------------------------------

-- (중요) 'sosohaeng_db' 스키마(데이터베이스)를 사용합니다.
USE `sosohaeng_db`;

-- 테이블 생성 전, 존재할 경우 삭제 (외래 키 제약 순서의 역순)
DROP TABLE IF EXISTS `market_wishlist`;
DROP TABLE IF EXISTS `market_qna`;
DROP TABLE IF EXISTS `market_product_images`;
DROP TABLE IF EXISTS `market_products`;
DROP TABLE IF EXISTS `market_users`;


-- 1. 사용자 (market_users)
CREATE TABLE `market_users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `hashed_password` VARCHAR(255) NOT NULL,
    `is_seller` BOOLEAN DEFAULT FALSE,
    `business_number` VARCHAR(50) UNIQUE,
    `seller_status` VARCHAR(20) DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- 2. 상품 (market_products)
CREATE TABLE `market_products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `price` INT NOT NULL DEFAULT 0,
    `shop_name` VARCHAR(100),
    `location` VARCHAR(255),
    `summary` TEXT,
    `seller_note` TEXT,
    `delivery_info` VARCHAR(255),
    `region` VARCHAR(50),
    `rating` DECIMAL(3, 2) DEFAULT 0.00,
    `likes` INT DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `market_users`(`id`)
);


-- 3. 상품 이미지 (market_product_images)
CREATE TABLE `market_product_images` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `image_url` VARCHAR(1024) NOT NULL,
    `is_thumbnail` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `market_products`(`id`) ON DELETE CASCADE
);


-- 4. 상품 문의 (market_qna)
CREATE TABLE `market_qna` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `author_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `body` TEXT NOT NULL,
    `answer_body` TEXT,
    `answered_by_id` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `answered_at` TIMESTAMP NULL,
    FOREIGN KEY (`product_id`) REFERENCES `market_products`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`author_id`) REFERENCES `market_users`(`id`),
    FOREIGN KEY (`answered_by_id`) REFERENCES `market_users`(`id`)
);


-- 5. 찜 목록 (market_wishlist)
CREATE TABLE `market_wishlist` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(`user_id`, `product_id`),
    FOREIGN KEY (`user_id`) REFERENCES `market_users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `market_products`(`id`) ON DELETE CASCADE
);



-- 인덱스 추가
CREATE INDEX `idx_products_region` ON `market_products`(`region`);
CREATE INDEX `idx_products_likes` ON `market_products`(`likes` DESC);
CREATE INDEX `idx_products_rating` ON `market_products`(`rating` DESC);
CREATE INDEX `idx_product_images_product_id` ON `market_product_images`(`product_id`);
CREATE INDEX `idx_product_qna_product_id` ON `market_qna`(`product_id`);
CREATE INDEX `idx_wishlist_user_id` ON `market_wishlist`(`user_id`);