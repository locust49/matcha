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
-- Table db_matcha.`password_reset_tokens`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS password_reset_tokens (
  "user_id" uuid NOT NULL REFERENCES users("uuid"),
  "token" VARCHAR(128) NOT NULL UNIQUE,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("user_id", "token")
);


-- -----------------------------------------------------
-- Enum types gender_enum && orientation_enum
-- For profiles table
-- -----------------------------------------------------

CREATE TYPE "gender_enum" AS ENUM ('FEMALE', 'MALE', 'BI');

CREATE TYPE "orientation_enum" AS ENUM ('HETERO', 'HOMO', 'BI');


-- -----------------------------------------------------
-- Table db_matcha.`profiles`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS profiles
(
    "uuid" uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    "user_id" uuid NOT NULL REFERENCES users("uuid"),
    "date_of_birth" TIMESTAMP NOT NULL,
    "fame_rating" NUMERIC(2, 2) NOT NULL DEFAULT 0 CHECK ("fame_rating" >= 0 AND "fame_rating" <= 1),
    "is_online" BOOLEAN DEFAULT FALSE,
    "last_login" TIMESTAMP,
    "location" POINT NOT NULL,
    "gender" gender_enum NOT NULL,
    "orientation" orientation_enum NOT NULL DEFAULT 'Bi',
    "biography" varchar(500)
);


-- -----------------------------------------------------
-- Table db_matcha.`images`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS images
(
    "uuid" uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    "profile_id" uuid NOT NULL REFERENCES profiles("uuid")
);


-- -----------------------------------------------------
-- Alter table db_matcha.`profiles` to add column `profile_pic`
-- -----------------------------------------------------


ALTER TABLE profiles ADD COLUMN "image_primary_id" uuid NOT NULL REFERENCES images("uuid");