import pandas as pd
import oracledb
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    try:
        connection = oracledb.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=os.getenv("ORACLE_DSN")
        )
        logger.info("Database connection established")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def execute_query(query: str) -> pd.DataFrame:
    connection = get_db_connection()
    try:
        df = pd.read_sql(query, connection)
        logger.info(f"Query executed successfully. Rows: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        connection.close()


def export_to_spreadsheet(df: pd.DataFrame, filename: str):
    output_dir = Path(filename).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        logger.info(f"Data exported to {filename}")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise


def run_extraction_pipeline():
    queries = {
        "budget_execution": """
            select * from fct_budget_execution
        """,
        "anomalies": """
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
            select * from moving_average
            where total_amount > (moving_avg_3m * 1.5)
        """
    }
    
    logger.info("Starting extraction pipeline")
    
    for name, query in queries.items():
        try:
            logger.info(f"Extracting {name}...")
            df = execute_query(query)
            export_to_spreadsheet(df, f"output/{name}.xlsx")
        except Exception as e:
            logger.error(f"Failed to process {name}: {e}")
            continue
    
    logger.info("Extraction pipeline completed")


if __name__ == "__main__":
    run_extraction_pipeline()
