"""
demo/run_demo.py

Main entry point for the AI Tinkerers SP live demo.
Runs the full pipeline in 3 beats:

  BEAT 1 - Show raw data structure (simulating Oracle/SIGEO extraction)
  BEAT 2 - Show dbt transformation output (fct_budget_execution)
  BEAT 3 - Gemini LLM analysis: narrative + anomaly alert

Usage:
  python demo/run_demo.py                  # runs full demo
  python demo/run_demo.py --beat 1         # runs only beat 1
  python demo/run_demo.py --beat 3         # runs only beat 3 (requires API key)
  python demo/run_demo.py --anomaly-only   # runs anomaly alerts on flagged records
"""

import sys
import time
import argparse
sys.path.insert(0, ".")

from demo.sample_data import SAMPLE_RECORDS, ANOMALY_RECORDS, NARRATIVE_RECORD
from src.llm_narrative import generate_narrative, batch_analyze


BANNER = """
================================================================
  SP GOVERNMENT BUDGET ANALYTICS - AI TINKERERS SP DEMO
  Oracle + SIGEO + dbt + Gemini LLM
  github.com/bellDataSc/sp-gov-budget-analytics
================================================================
"""


def print_section(title: str) -> None:
    print(f"\n{'='*64}")
    print(f"  {title}")
    print(f"{'='*64}")


def beat_1_raw_data() -> None:
    """BEAT 1 - Raw data from Oracle/SIGEO before transformation."""
    print_section("BEAT 1 | RAW DATA - Oracle DB via SIGEO/MF")
    print("""
Context: This data was originally extracted from Oracle Database
connected to SIGEO (Sistema de Informacoes Gerenciais e de
Planejamento - Ministry of Finance) while working for the
Sao Paulo State Government Budget Planning Management.

Raw fields in the Oracle source table:
  - NR_EMPENHO       (commitment number)
  - CD_ORGAO         (agency code)
  - DS_CATEGORIA     (expenditure category description)
  - VL_DOTACAO       (authorized budget)
  - VL_EMPENHADO     (committed amount)
  - VL_PAGO          (paid amount)
  - DT_REFERENCIA    (reference date)
  - CD_FONTE_RECURSO (funding source code)

The challenge: thousands of rows per month, multiple agencies,
no automated anomaly detection, manual Excel-based reporting.
""")
    print("Sample raw record (pre-dbt):")
    raw = SAMPLE_RECORDS[3]  # Critical spike record
    for k, v in raw.items():
        print(f"  {k:<28}: {v}")
    print()
    input("  [ENTER to continue to Beat 2...]")


def beat_2_dbt_output() -> None:
    """BEAT 2 - Transformed output from dbt mart (fct_budget_execution)."""
    print_section("BEAT 2 | dbt TRANSFORMATION - fct_budget_execution mart")
    print("""
After dbt pipeline runs:
  - stg_budget_transactions  : type casting, column naming, source filtering
  - fct_budget_execution     : monthly aggregation, window functions,
                               moving averages, deviation calculation,
                               anomaly flag logic

Key SQL techniques used (Oracle-native):
  - ROUND(AVG(vl_pago) OVER (ORDER BY periodo
      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)  AS media_movel_3m
  - CASE WHEN desvio_percentual > 20 THEN 'HIGH_DEVIATION'
         WHEN taxa_execucao < 50     THEN 'LOW_EXECUTION'
         WHEN desvio_percentual > 80 THEN 'CRITICAL_SPIKE'
         ELSE 'NONE' END             AS flag_anomalia
  - XMLELEMENT / XMLAGG for XML extraction to SIGEO reporting format
""")
    print(f"Total records in mart output : {len(SAMPLE_RECORDS)}")
    print(f"Records with anomaly flags   : {len(ANOMALY_RECORDS)}")
    print()
    print("Anomaly distribution:")
    from collections import Counter
    flags = Counter(r["flag_anomalia"] for r in SAMPLE_RECORDS)
    for flag, count in flags.items():
        print(f"  {flag:<25}: {count} record(s)")
    print()
    input("  [ENTER to continue to Beat 3 - Gemini LLM...]")


def beat_3_llm(anomaly_only: bool = False) -> None:
    """BEAT 3 - Gemini LLM generates economic narratives and anomaly alerts."""
    print_section("BEAT 3 | GEMINI LLM - Economic Narrative + Anomaly Alerts")
    print("""
The key technique (reusable by any builder):

  1. dbt mart output -> Python dict (structured context)
  2. build_budget_context() serializes it into a human-readable block
  3. build_prompt() injects context into a role-specific prompt:
       - Role: senior public finance analyst, Brazil
       - Task: narrative OR anomaly alert
       - Data: the structured budget block
  4. Gemini 1.5 Flash returns analysis in Portuguese
     without any fine-tuning - pure context engineering.

No fine-tuning. No RAG. Just structured context + clear role.
""")

    if anomaly_only:
        print(f"Running anomaly alerts on {len(ANOMALY_RECORDS)} flagged records...\n")
        batch_analyze(ANOMALY_RECORDS, analysis_type="anomaly")
    else:
        print("Step 3a: Narrative analysis on a healthy record...")
        generate_narrative(NARRATIVE_RECORD, analysis_type="narrative")
        time.sleep(1)

        print("\nStep 3b: Anomaly alert on the CRITICAL_SPIKE record...")
        critical = next(r for r in SAMPLE_RECORDS if r["flag_anomalia"] == "CRITICAL_SPIKE")
        generate_narrative(critical, analysis_type="anomaly")


def run_full_demo(anomaly_only: bool = False) -> None:
    print(BANNER)
    beat_1_raw_data()
    beat_2_dbt_output()
    beat_3_llm(anomaly_only=anomaly_only)
    print_section("DEMO COMPLETE")
    print("""
Builder takeaway:
  - Any structured dataset + dbt + context-rich prompting = LLM analyst
  - No fine-tuning needed for domain-specific interpretation
  - Pattern: transform -> serialize -> prompt -> interpret
  - Replicable with any relational DB, not just Oracle/government data

  github.com/bellDataSc/sp-gov-budget-analytics
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Tinkerers SP - Budget Analytics Demo")
    parser.add_argument("--beat", type=int, choices=[1, 2, 3], help="Run a specific beat only")
    parser.add_argument("--anomaly-only", action="store_true", help="Run anomaly alerts only in beat 3")
    args = parser.parse_args()

    if args.beat == 1:
        beat_1_raw_data()
    elif args.beat == 2:
        beat_2_dbt_output()
    elif args.beat == 3:
        beat_3_llm(anomaly_only=args.anomaly_only)
    else:
        run_full_demo(anomaly_only=args.anomaly_only)
