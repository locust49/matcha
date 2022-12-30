CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SET TIME ZONE 'UTC';

-- -----------------------------------------------------
-- Table db_matcha.`users`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
  "uuid" uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  "username" VARCHAR(20) NOT NULL UNIQUE,
  "password" TEXT NOT NULL,
  "email" VARCHAR(50) NOT NULL UNIQUE,
  "first_name" VARCHAR(20) NOT NULL,
  "last_name" VARCHAR(20) NOT NULL,
  "verified" BOOLEAN NOT NULL DEFAULT FALSE,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- Insert data into table `DB_NAME`.`users`
-- -----------------------------------------------------
-- INSERT INTO users (username, email, password, first_name, last_name)
-- VALUES ('admin', 'admin@admin.ma' , 'admin', 'admin', 'admin');


CREATE TABLE IF NOT EXISTS password_reset_tokens (
  "user_id" uuid NOT NULL,
  "token" VARCHAR(128) NOT NULL UNIQUE,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("user_id", "token"),
  FOREIGN KEY ("user_id") REFERENCES users("uuid")
);
