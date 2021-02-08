CREATE VIEW txs_queue AS (
    SELECT
        transaction.block,
        eth_txhash,
        cyber_hash,
        cyber,
        eth,
        eul,
        sum(eth) OVER (ORDER BY block.block, index) as eth_sum,
        sum(eul) OVER (ORDER BY block.block, index) :: bigint as eul_sum,
        (eth / eul) * 1000000000 as av_price,
        checked,
        sender,
        sum(eth) OVER (PARTITION BY sender) as eth_sum_by_address,
        sum(eul) OVER (PARTITION BY sender) :: bigint as eul_sum_by_address,
        block.block_time
    FROM transaction
    LEFT JOIN block
    ON block.block = transaction.block
);

CREATE VIEW day_price AS (
    SELECT
        coalesce(max(av_price), 0.1) as day
    FROM
        txs_queue
    WHERE block_time <= extract(epoch from now()) - 24*60*60
);

CREATE VIEW week_price AS (
    SELECT
        coalesce(max(av_price), 0.1) as week
    FROM
        txs_queue
    WHERE block_time <= extract(epoch from now()) - 24*60*60*7
);

CREATE VIEW month_price AS (
    SELECT
        coalesce(max(av_price), 0.1) as month
    FROM
        txs_queue
    WHERE block_time <= extract(epoch from now()) - 24*60*60*30
);


CREATE VIEW market_data AS (
    SELECT
        coalesce(sum(eth),0) as eth_donated,
        coalesce(max(av_price),0.1) as last_price,
        coalesce(sum(eul),0) as euls_won,
        coalesce((0.1 + 0.000198 * (sum(eul)/1000000000)), 0.1) as current_price,
        coalesce((0.1 + 0.000198 * (sum(eul)/1000000000)) * 1000000, 0.1 * 1000000) as market_cap_eth
    FROM
        txs_queue
);