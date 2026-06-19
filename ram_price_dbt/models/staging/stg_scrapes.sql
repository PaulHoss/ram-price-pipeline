-- Silver layer: clean and validate raw Bronze scrapes
-- Filters out pipeline failures, casts types, standardizes fields

with source as (
    select *
    from ram_price_tracker.bronze_scrapes
),

cleaned as (
    select
        mpn,
        brand,
        gen,
        model,
        marketplace,
        seller,
        cast(price as double)           as price,
        currency,
        availability,
        condition,
        cast(date as date)              as price_date,
        date_parse(substr(timestamp, 1, 26), '%Y-%m-%dT%H:%i:%S.%f') as scraped_at,
        pipeline_status,
        url_fetch_method,
        scraped_title
    from source
    where pipeline_status = 'Pass'
      and price is not null
      and mpn is not null
)

select * from cleaned