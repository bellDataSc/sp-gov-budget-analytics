"""
demo/sample_data.py

Anonymized budget execution records representative of the
Sao Paulo State Government data originally extracted from
Oracle Database via SIGEO (Sistema de Informacoes Gerenciais
e de Planejamento - Ministry of Finance).

All values are synthetic and scaled to preserve structural
patterns without exposing real government data.
"""

# Records output from fct_budget_execution dbt mart
# Schema mirrors the dimensional model built on Oracle
SAMPLE_RECORDS = [
    {
        # Normal execution - healthy spending pattern
        "periodo_referencia": "2023-07",
        "orgao": "Secretaria de Educacao",
        "categoria_despesa": "Pessoal e Encargos Sociais",
        "dotacao_autorizada": 45_000_000.00,
        "valor_empenhado": 43_200_000.00,
        "valor_pago": 42_100_000.00,
        "taxa_execucao": 96.0,
        "media_movel_3m": 42_500_000.00,
        "desvio_percentual": +1.6,
        "flag_anomalia": "NONE",
        "sistema_origem": "SIGEO/MF",
    },
    {
        # High deviation - potential overspend in discretionary category
        "periodo_referencia": "2023-08",
        "orgao": "Secretaria da Fazenda e Planejamento",
        "categoria_despesa": "Custeio - Servicos de Terceiros",
        "dotacao_autorizada": 12_500_000.00,
        "valor_empenhado": 11_875_000.00,
        "valor_pago": 9_100_000.00,
        "taxa_execucao": 95.0,
        "media_movel_3m": 8_200_000.00,
        "desvio_percentual": +11.0,
        "flag_anomalia": "HIGH_DEVIATION",
        "sistema_origem": "SIGEO/MF",
    },
    {
        # Low execution - budget underutilization alert
        "periodo_referencia": "2023-09",
        "orgao": "Secretaria de Infraestrutura e Meio Ambiente",
        "categoria_despesa": "Investimentos - Obras e Instalacoes",
        "dotacao_autorizada": 38_000_000.00,
        "valor_empenhado": 14_060_000.00,
        "valor_pago": 8_900_000.00,
        "taxa_execucao": 37.0,
        "media_movel_3m": 24_000_000.00,
        "desvio_percentual": -41.4,
        "flag_anomalia": "LOW_EXECUTION",
        "sistema_origem": "SIGEO/MF",
    },
    {
        # Critical anomaly - spike in a single month vs rolling average
        "periodo_referencia": "2023-10",
        "orgao": "Secretaria da Saude",
        "categoria_despesa": "Custeio - Material de Consumo",
        "dotacao_autorizada": 9_800_000.00,
        "valor_empenhado": 9_600_000.00,
        "valor_pago": 9_500_000.00,
        "taxa_execucao": 98.0,
        "media_movel_3m": 5_100_000.00,
        "desvio_percentual": +86.3,
        "flag_anomalia": "CRITICAL_SPIKE",
        "sistema_origem": "SIGEO/MF",
    },
    {
        # End-of-year spending surge - common in public sector
        "periodo_referencia": "2023-12",
        "orgao": "Secretaria de Seguranca Publica",
        "categoria_despesa": "Custeio - Servicos de Terceiros",
        "dotacao_autorizada": 22_000_000.00,
        "valor_empenhado": 21_560_000.00,
        "valor_pago": 19_800_000.00,
        "taxa_execucao": 98.0,
        "media_movel_3m": 15_300_000.00,
        "desvio_percentual": +29.4,
        "flag_anomalia": "HIGH_DEVIATION",
        "sistema_origem": "SIGEO/MF",
    },
]

# Subset for quick live demo (anomaly cases only)
ANOMALY_RECORDS = [
    r for r in SAMPLE_RECORDS if r["flag_anomalia"] != "NONE"
]

# Single record for narrative generation demo beat
NARRATIVE_RECORD = SAMPLE_RECORDS[0]
