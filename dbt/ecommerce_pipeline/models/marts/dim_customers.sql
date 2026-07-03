
with customers as (
    select * from {{ ref('stg_olist__customers') }}
),

orders as (
    select * from {{ ref ('fct_orders') }}
),

customer_orders as (
    select
        customer_id,
        count(order_id) as total_orders,
        sum(payment_total) as total_spend,
        min(order_purchase_at) as first_order_at,
        max(order_purchase_at) as last_order_at
    from orders
    group by customer_id
),

final as (
    select
        c.customer_id,
        c.customer_city,
        c.customer_state,
        coalesce(co.total_orders, 0) as total_orders,
        coalesce(co.total_spend, 0) as total_spend,
        co.first_order_at,
        co.last_order_at
    from customers c 
    left join customer_orders co on c.customer_id = co.customer_id
)

select * from final