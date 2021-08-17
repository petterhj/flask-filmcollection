-- upgrade --
CREATE TABLE IF NOT EXISTS "film" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "summary" TEXT,
    "release_date" DATE,
    "tmdb_id" VARCHAR(15) NOT NULL UNIQUE,
    "imdb_id" VARCHAR(15)  UNIQUE
);
CREATE TABLE IF NOT EXISTS "release" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "release_format" VARCHAR(3) NOT NULL  /* VHS: VHS\nDVD: DVD\nBD: BD\nUHD: UHD */,
    "barcode" VARCHAR(25),
    "added_date" DATE,
    "film_id" INT NOT NULL REFERENCES "film" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
