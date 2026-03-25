import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Gemini API
# Set GEMINI_API_KEY in your .env file before running
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def build_budget_context(budget_data: dict) -> str:
    """
    Serializes structured budget execution data into a formatted string
    to be injected as context in the LLM prompt.

    Args:
        budget_data: dict with keys from fct_budget_execution mart output

    Returns:
        Formatted string context for the LLM
    """
    lines = [
        f"Reference Period     : {budget_data.get('periodo_referencia', 'N/A')}",
        f"Government Agency    : {budget_data.get('orgao', 'N/A')}",
        f"Expenditure Category : {budget_data.get('categoria_despesa', 'N/A')}",
        f"Authorized Budget    : R$ {budget_data.get('dotacao_autorizada', 0):,.2f}",
        f"Executed Budget      : R$ {budget_data.get('valor_empenhado', 0):,.2f}",
        f"Paid Amount          : R$ {budget_data.get('valor_pago', 0):,.2f}",
        f"Execution Rate       : {budget_data.get('taxa_execucao', 0):.1f}%",
        f"3-Month Moving Avg   : R$ {budget_data.get('media_movel_3m', 0):,.2f}",
        f"Deviation from Avg   : {budget_data.get('desvio_percentual', 0):+.1f}%",
        f"Anomaly Flag         : {budget_data.get('flag_anomalia', 'NONE')}",
        f"SIGEO Source System  : {budget_data.get('sistema_origem', 'SIGEO/MF')}",
    ]
    return "\n".join(lines)


def build_prompt(budget_context: str, analysis_type: str = "narrative") -> str:
    """
    Constructs the prompt template for the Gemini model.
    Two modes:
      - 'narrative': generates an economic narrative paragraph
      - 'anomaly': generates a structured anomaly alert

    Args:
        budget_context: formatted string from build_budget_context()
        analysis_type: 'narrative' or 'anomaly'

    Returns:
        Full prompt string ready to send to Gemini
    """
    base_instructions = (
        "You are a senior public finance analyst specializing in Brazilian state government budgets. "
        "You receive structured data extracted from Oracle Database via SIGEO "
        "(Sistema de Informacoes Gerenciais e de Planejamento - Ministry of Finance) "
        "and transformed through a dbt analytical pipeline. "
        "Write in Portuguese (Brazil). Be concise, technical, and objective. "
        "Do not invent numbers. Only interpret what is given."
    )

    if analysis_type == "narrative":
        task = (
            "Based on the budget execution data below, write a 3-sentence economic narrative "
            "suitable for a public policy report. Include the execution rate assessment, "
            "comparison with the moving average, and a brief recommendation for the budget manager."
        )
    elif analysis_type == "anomaly":
        task = (
            "Based on the budget execution data below, generate a structured anomaly alert. "
            "Format the output as:\n"
            "ANOMALY LEVEL: [LOW / MEDIUM / HIGH / CRITICAL]\n"
            "IMPACTED AGENCY: <agency name>\n"
            "PERIOD: <period>\n"
            "FINDING: <one sentence describing the anomaly>\n"
            "RECOMMENDED ACTION: <one sentence with the recommended next step>"
        )
    else:
        raise ValueError(f"Unknown analysis_type: '{analysis_type}'. Use 'narrative' or 'anomaly'.")

    prompt = f"{base_instructions}\n\n{task}\n\nBUDGET DATA:\n{budget_context}"
    return prompt


def generate_narrative(budget_data: dict, analysis_type: str = "narrative") -> str:
    """
    Main function: takes budget data dict, builds the prompt,
    calls Gemini API, and returns the generated text.

    Args:
        budget_data: dict with budget execution metrics
        analysis_type: 'narrative' or 'anomaly'

    Returns:
        Generated text from Gemini
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    context = build_budget_context(budget_data)
    prompt = build_prompt(context, analysis_type)

    print(f"\n{'='*60}")
    print(f"ANALYSIS TYPE : {analysis_type.upper()}")
    print(f"AGENCY        : {budget_data.get('orgao', 'N/A')}")
    print(f"PERIOD        : {budget_data.get('periodo_referencia', 'N/A')}")
    print(f"{'='*60}")
    print("Calling Gemini API...\n")

    response = model.generate_content(prompt)
    result = response.text.strip()

    print("GEMINI OUTPUT:")
    print("-" * 60)
    print(result)
    print("-" * 60)

    return result


def batch_analyze(records: list[dict], analysis_type: str = "narrative") -> list[dict]:
    """
    Processes a list of budget records and returns enriched records
    with the LLM-generated analysis attached.

    Args:
        records: list of budget data dicts
        analysis_type: 'narrative' or 'anomaly'

    Returns:
        List of dicts with original data + 'llm_analysis' key
    """
    results = []
    for i, record in enumerate(records, 1):
        print(f"\nProcessing record {i}/{len(records)}...")
        try:
            analysis = generate_narrative(record, analysis_type)
            results.append({**record, "llm_analysis": analysis, "analysis_type": analysis_type})
        except Exception as e:
            print(f"ERROR on record {i}: {e}")
            results.append({**record, "llm_analysis": f"ERROR: {e}", "analysis_type": analysis_type})
    return results


if __name__ == "__main__":
    # Quick smoke test with a single synthetic record
    sample = {
        "periodo_referencia": "2023-09",
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
    }

    print("Running narrative analysis...")
    generate_narrative(sample, analysis_type="narrative")

    print("\nRunning anomaly alert analysis...")
    generate_narrative(sample, analysis_type="anomaly")
