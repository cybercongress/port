-- Table Definition ----------------------------------------------

CREATE TABLE block (
    block integer NOT NULL UNIQUE PRIMARY KEY,
    block_time integer,
    checked boolean
);