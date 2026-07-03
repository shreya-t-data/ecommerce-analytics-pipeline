
with orders as (
    select * from {{ ref('stg_olist__orders') }}
),

order_items as (
    select * from {{ ref('stg_olist__order_items') }}
),

payments as (
    select * from {{ ref('stg_olist__order_payments') }}
),

item_totals as (
    select 
        order_id,
        sum(price) as items_total,
        sum(freight_value) as freight_total,
        count(*) as item_count
    from order_items
    group by order_id
),

payment_totals as (
    select
        order_id,
        sum(payment_value) as payment_total
    from payments
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_at,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        it.item_count,
        it.items_total,
        it.freight_total,
        pt.payment_total,
        extract(epoch from (o.order_delivered_customer_date - o.order_purchase_at)) / 86400.0
            as delivery_days
    
    from orders o 
    left join item_totals it on o.order_id = it.order_id
    left join payment_totals pt on o.order_id = pt.order_id
)

select * from final