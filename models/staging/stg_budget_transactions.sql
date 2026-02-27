select
    transaction_id,
    entity_id,
    cast(transaction_date as date) as execution_date,
    cast(transaction_amount as number) as amount,
    transaction_type,
    status
from
    {{ source('sp_gov_raw', 'raw_financial_transactions') }}
where
    status is not null
