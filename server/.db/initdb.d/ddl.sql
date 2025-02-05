CREATE TABLE user_tb
(
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    google_id       VARCHAR(50)   NOT NULL UNIQUE,
    access_token    VARCHAR(255)  NOT NULL,
    refresh_token   VARCHAR(255)  NOT NULL,
    expiry          TIMESTAMP     NOT NULL,
    upstage_api_key VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE report_temp_tb
(
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT    NOT NULL,
    content      TEXT,
    date         DATE      NOT NULL,
    refresh_time TIMESTAMP NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
