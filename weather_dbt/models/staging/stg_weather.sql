with source as (
    select * from raw_weather
),

cleaned as (
    select
        city,
        cast(date as date)              as date,
        latitude,
        longitude,
        temperature_2m_max              as temp_max_c,
        temperature_2m_min              as temp_min_c,
        round((temperature_2m_max + temperature_2m_min) / 2, 2) as temp_avg_c,
        coalesce(precipitation_sum, 0)  as precipitation_mm,
        windspeed_10m_max               as windspeed_max_kmh,
        sunrise,
        sunset,
        ingested_at
    from source
    where date is not null
)

select * from cleaned