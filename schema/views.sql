CREATE VIEW txs_queue AS (
    SELECT
        transaction.block
        eth_txhash,
        cyber_hash,
        cyber,
        eth,
        eul,
        sum(eth) OVER (ORDER BY block.block, index) as eth_sum,
        sum(eul) OVER (ORDER BY block.block, index) :: bigint as eul_sum,
        (eth / eul) * 1000000000 as av_price,
        checked
    FROM transaction
    LEFT JOIN block
    ON block.block = transaction.block
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