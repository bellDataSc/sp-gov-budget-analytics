with staging_transactions as (
    select
        transaction_id,
        entity_id,
        execution_date,
        amount,
        transaction_type
    from
        {{ ref('stg_budget_transactions') }}
)

select
    entity_id,
    trunc(execution_date, 'MM') as execution_month,
    transaction_type,
    sum(amount) as total_executed_amount,
    count(transaction_id) as transaction_count
from
    staging_transactions
group by
    entity_id,
    trunc(execution_date, 'MM'),
    transaction_type
