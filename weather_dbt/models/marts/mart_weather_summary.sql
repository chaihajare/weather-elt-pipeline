with daily as (
    select * from {{ ref('int_weather_daily') }}
),

summary as (
    select
        city,
        date,
        temp_max_c,
        temp_min_c,
        temp_avg_c,
        precipitation_mm,
        windspeed_max_kmh,
        temp_category,
        precipitation_category,
        avg(temp_avg_c) over (
            partition by city
            order by date
            rows between 6 preceding and current row
        ) as temp_7day_rolling_avg,
        sum(precipitation_mm) over (
            partition by city
            order by date
            rows between 6 preceding and current row
        ) as precipitation_7day_rolling_sum
    from daily
)

select * from summary
order by city, date