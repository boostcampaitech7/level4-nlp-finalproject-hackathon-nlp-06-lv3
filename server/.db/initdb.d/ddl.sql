CREATE TABLE user_tb
(
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    google_id     VARCHAR(50)   NOT NULL UNIQUE,
    access_token  VARCHAR(255)  NOT NULL,
    refresh_token VARCHAR(255)  NOT NULL,
    expiry        TIMESTAMP     NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE report_tb
(
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT    NOT NULL,
    body       TEXT,
    start      TIMESTAMP NOT NULL,
    end        TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
