-- Gold layer: analytics-ready fact table
-- One row per product + marketplace + date
-- Adds price change delta vs prior day

with silver as (
    select * from {{ ref('stg_scrapes') }}
),

with_lag as (
    select
        *,
        lag(price) over (
            partition by mpn, marketplace
            order by price_date
        ) as prior_day_price
    from silver
),

final as (
    select
        mpn,
        brand,
        gen,
        model,
        marketplace,
        seller,
        price,
        currency,
        availability,
        price_date,
        scraped_at,
        prior_day_price,
        round(price - prior_day_price, 2)                          as price_change,
        round((price - prior_day_price) / prior_day_price * 100, 2) as price_change_pct,
        rank() over (
            partition by gen, price_date
            order by price asc
        ) as price_rank_within_gen
    from with_lag
)

select * from final