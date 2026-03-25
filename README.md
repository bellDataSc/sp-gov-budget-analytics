# SP Government Budget Analytics

**ps: this is v2. I decided to better document the old process and add new perspectives, hence the new repository. I'm always using my GitHub as a personal document for advancing technology in the data universe.**

In this repository, I documented an analytical engineering framework designed for public sector financial data. The architecture uses SQL and dbt (Data Build Tool) to transform raw financial records into a dimensional model. Working with data engineering, I developed and applied this methodology to monitor public spending, detect financial anomalies, and optimize processes in the Budget Planning Management of the State Government of São Paulo.

During the execution of this project, the main processing was performed in an Oracle database environment. I used advanced SQL filtering techniques to process the data and subsequently translated the selected datasets into XML format, necessary for creating data spreadsheets and performing the final extractions.

## Architecture and Methodology

The project follows modern analytical engineering practices, using a multi-layered approach to ensure data reliability and financial compliance:

- **Staging Layer**: Extracts raw data from the data warehouse, converting data types and standardizing column naming conventions.
- **Marts Layer**: Aggregates financial transactions into fact tables, creating the semantic layer consumed by subsequent Business Intelligence platforms.
- **Automated Testing**: Implements primary key uniqueness and non-nullability constraints to ensure absolute fidelity of public metrics.
- **XML Data Extraction**: Utilizes Oracle XML DB functionalities to generate well-formed XML structures directly from relational tables for later consumption.

## Project Structure

```
sp-gov-budget-analytics/
├── models/
│   ├── staging/
│   │   ├── schema.yml
│   │   └── stg_budget_transactions.sql
│   └── marts/
│       └── fct_budget_execution.sql
├── scripts/
│   ├── xml_extraction.sql
│   └── advanced_anomaly_detection.sql
├── src/
│   └── extract_metrics_to_excel.py
├── dbt_project.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and Installation

### Prerequisites

- Python 3.9+
- dbt 1.5+
- Oracle Database 19c+
- Oracle Python client (oracledb)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/bellDataSc/sp-gov-budget-analytics.git
cd sp-gov-budget-analytics
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure Oracle connection in `~/.dbt/profiles.yml`:

```yaml
sp_gov_oracle:
  target: dev
  outputs:
    dev:
      type: oracle
      user: [your_user]
      pass: [your_password]
      database: [your_database]
      schema: analytics
      threads: 4
```

4. Set environment variables:

```bash
export ORACLE_USER=your_user
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=your_dsn_string
```

### Running the Pipeline

1. Execute dbt models:

```bash
dbt run
dbt test
```

2. Extract metrics to Excel:

```bash
python src/extract_metrics_to_excel.py
```

Output files will be generated in the `output/` directory.

## Key Components

### dbt Models

- `stg_budget_transactions`: Staging layer with data type conversions and standardization
- `fct_budget_execution`: Fact table aggregating monthly budget execution metrics

### SQL Scripts

- `xml_extraction.sql`: Native Oracle XML generation from dimensional tables
- `advanced_anomaly_detection.sql`: Window functions for anomaly detection with XML output

### Python Pipeline

- `extract_metrics_to_excel.py`: Modular extraction and Excel export functionality

## Advanced SQL Techniques

This project demonstrates advanced SQL capabilities:

- Window functions (moving averages, row ranking)
- Common Table Expressions (CTEs) for complex aggregations
- Native Oracle XML functions (XMLELEMENT, XMLFOREST, XMLAGG)
- Dynamic SQL generation with dbms_xmlgen
- Anomaly detection using statistical methods

## Data Compliance

All metrics are tested for:

- Primary key uniqueness
- Non-null constraints on critical dimensions
- Referential integrity across staging and marts layers
- Data freshness and completeness

---

Made with coffee and data by Isabel Cruz

---

## AI Tinkerers SP Demo — March 2026

> **Talk:** *From Oracle to Insight: How I Built an AI-Augmented Budget Intelligence Pipeline for the São Paulo State Government*

This repository includes a fully runnable demo built for [AI Tinkerers SP](https://aitinkerers.org) + Banco BMG (March 26, 2026).
The demo shows how to layer Gemini LLM on top of a real government data pipeline — no fine-tuning, pure context engineering.

### The 3-Beat Structure

| Beat | What happens |
|------|--------------|
| **Beat 1** | Raw Oracle/SIGEO data structure — the original problem |
| **Beat 2** | dbt transformation output (`fct_budget_execution`) — anomaly flags, moving averages |
| **Beat 3** | Gemini 1.5 Flash generates economic narratives and anomaly alerts in Portuguese |

### Running the Demo

**Prerequisites:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
# Get a free key at: https://aistudio.google.com/app/apikey
```

**Full demo (interactive, 3 beats):**
```bash
python demo/run_demo.py
```

**Single beat:**
```bash
python demo/run_demo.py --beat 1   # Raw data structure
python demo/run_demo.py --beat 2   # dbt output
python demo/run_demo.py --beat 3   # Gemini analysis
```

**Anomaly alerts only:**
```bash
python demo/run_demo.py --anomaly-only
```

### Builder Takeaway

The reusable pattern (works with any relational database):

```
Oracle/SIGEO -> dbt (transform) -> Python dict -> Gemini prompt -> Economic narrative
```

- `src/llm_narrative.py` — core LLM layer with `generate_narrative()` and `batch_analyze()`
- `demo/sample_data.py` — anonymized budget records mirroring Oracle schema
- `demo/run_demo.py` — interactive demo runner

Key insight: **structured context + clear analyst role = domain-specific LLM analysis without fine-tuning.**

---

Made with coffee and data by Isabel Cruz
