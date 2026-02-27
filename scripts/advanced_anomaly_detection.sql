with monthly_execution as (
    select
        entity_id,
        trunc(execution_date, 'MM') as exec_month,
        sum(amount) as total_amount
    from
        stg_budget_transactions
    group by
        entity_id,
        trunc(execution_date, 'MM')
),
moving_average as (
    select
        entity_id,
        exec_month,
        total_amount,
        avg(total_amount) over (
            partition by entity_id
            order by exec_month
            rows between 2 preceding and current row
        ) as moving_avg_3m
    from
        monthly_execution
)
select
    xmlelement("AnomalyReport",
        xmlagg(
            xmlelement("Record",
                xmlforest(
                    entity_id as "EntityID",
                    to_char(exec_month, 'YYYY-MM-DD') as "Month",
                    total_amount as "Amount",
                    moving_avg_3m as "MovingAverage"
                )
            )
        )
    ).getClobVal()
from
    moving_average
where
    total_amount > (moving_avg_3m * 1.5)
