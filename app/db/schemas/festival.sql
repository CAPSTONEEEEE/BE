-- 1. 프로젝트를 대표하는 데이터베이스 생성
-- (만약 이미 있다면 오류를 피하기 위해 IF NOT EXISTS를 사용)
CREATE DATABASE IF NOT EXISTS sosohaeng_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 이제부터 이 DB 안에서 작업하겠다고 선언
USE sosohaeng_db;

-- 3. festivals 테이블 생성 쿼리를 여기에 붙여넣어 실행
CREATE TABLE festivals (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'DB 내부에서 사용하는 고유 ID',
    contentid VARCHAR(10) NOT NULL UNIQUE COMMENT 'TourAPI의 콘텐츠 ID',
    title VARCHAR(255) NOT NULL COMMENT '축제 이름',
    addr1 VARCHAR(255) COMMENT '주소',
    event_start_date VARCHAR(8) COMMENT '행사 시작일 (YYYYMMDD)',
    event_end_date VARCHAR(8) COMMENT '행사 종료일 (YYYYMMDD)',
    mapx DECIMAL(10, 7) NOT NULL COMMENT '경도',
    mapy DECIMAL(10, 7) NOT NULL COMMENT '위도',
    image_url VARCHAR(500) COMMENT '대표 이미지 URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_map_coords (mapx, mapy)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='TourAPI 축제 정보 테이블';

DESCRIBE festivals;