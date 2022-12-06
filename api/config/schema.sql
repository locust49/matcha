CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------
-- Table db_matcha.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
  "uuid" uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
  "username" VARCHAR(20) NOT NULL UNIQUE,
  "password" TEXT NOT NULL,
  "email" VARCHAR(50) NOT NULL UNIQUE,
  "first_name" VARCHAR(20) NOT NULL,
  "last_name" VARCHAR(20) NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------
-- Insert data into table `DB_NAME`.`users`
-- -----------------------------------------------------
INSERT INTO users (username, email, password, first_name, last_name)
VALUES ('admin', 'admin@admin.ma' , 'admin', 'admin', 'admin');


