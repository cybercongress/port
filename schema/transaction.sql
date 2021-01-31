-- Table Definition ----------------------------------------------

CREATE TABLE transaction (
    eth_txhash character varying(66) NOT NULL UNIQUE PRIMARY KEY,
    block integer NOT NULL,
    index integer NOT NULL,
    sender character varying(42) NOT NULL,
    cyber character varying(44) NOT NULL,
    eth real NOT NULL,
    cyber_hash character varying(64) UNIQUE,
    eul bigint
);