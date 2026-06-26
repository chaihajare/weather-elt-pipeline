with staged as (
    select * from {{ ref('stg_weather') }}
),

enriched as (
    select
        city,
        date,
        latitude,
        longitude,
        temp_max_c,
        temp_min_c,
        temp_avg_c,
        precipitation_mm,
        windspeed_max_kmh,
        sunrise,
        sunset,
        ingested_at,
        case
            when temp_max_c >= 35 then 'extreme_heat'
            when temp_max_c >= 25 then 'warm'
            when temp_max_c >= 15 then 'mild'
            when temp_max_c >= 5  then 'cool'
            else 'cold'
        end as temp_category,
        case
            when precipitation_mm > 10 then 'heavy_rain'
            when precipitation_mm > 2  then 'light_rain'
            else 'dry'
        end as precipitation_category
    from staged
)

select * from enriched