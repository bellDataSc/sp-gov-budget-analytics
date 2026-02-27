set long 50000
set pagesize 0
set heading off

select
    xmlelement("BudgetExecutions",
        xmlagg(
            xmlelement("Execution",
                xmlforest(
                    entity_id as "EntityID",
                    to_char(execution_month, 'YYYY-MM-DD') as "ExecutionMonth",
                    transaction_type as "TransactionType",
                    total_executed_amount as "TotalAmount",
                    transaction_count as "TransactionCount"
                )
            )
        )
    ).getClobVal()
from
    fct_budget_execution
