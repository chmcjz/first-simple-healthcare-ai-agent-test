from __future__ import annotations

import os
import re
from dotenv import load_dotenv
from ollama import Client

from data_loader import load_tables
import tools as T


def route_to_tool(user_text: str):
    """
    Deterministic routing so we never hallucinate IDs.
    Returns (tool_name, args) or (None, None).
    """
    s = user_text.strip()

    if re.search(r"\b(list|show)\s+tables\b", s, re.I):
        return "list_tables", {}

    if re.search(r"\b(schema|columns)\b", s, re.I):
        return "show_schema", {}

    m = re.search(r"\bsummary\s+(P\d+)\b", s, re.I)
    if m:
        return "patient_summary", {"patient_id": m.group(1).upper()}

    m = re.search(r"\blatest\s+([A-Za-z0-9]+)\s+for\s+(P\d+)\b", s, re.I)
    if m:
        test = m.group(1).upper()
        pid = m.group(2).upper()
        return "latest_lab", {"patient_id": pid, "test": test}

    m = re.search(r"\bICD\s*10\b.*\b([A-Z]\d{2})\b", s, re.I)
    if m:
        return "patients_by_icd10", {"icd10": m.group(1).upper()}

    m = re.search(r"\bfind\s+patient\s+(.+)$", s, re.I)
    if m:
        return "find_patient", {"name_contains": m.group(1).strip()}

    return None, None


def run_tool(tables, name: str, args: dict) -> str:
    if name == "list_tables":
        return T.list_tables(tables)
    if name == "show_schema":
        return T.show_schema(tables)
    if name == "find_patient":
        return T.find_patient(tables, args["name_contains"])
    if name == "patients_by_icd10":
        return T.patients_by_icd10(tables, args["icd10"])
    if name == "latest_lab":
        return T.latest_lab(tables, args["patient_id"], args["test"])
    if name == "patient_summary":
        return T.patient_summary(tables, args["patient_id"])
    return f"Unknown tool: {name}"


def llm_answer(client: Client, model: str, user_text: str) -> str:
    """
    For free-form questions that don't map to a tool.
    """
    system = (
        "You are a healthcare data assistant for a DEMO synthetic dataset.\n"
        "You must NOT provide medical advice, diagnosis, or treatment.\n"
        "If user asks for data facts, tell them to use commands like:\n"
        "list tables | show schema | patients with ICD10 E11 | summary P001 | latest A1C for P001\n"
    )
    resp = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
    )
    return resp["message"]["content"]


def main():
    load_dotenv()
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    client = Client(host="http://localhost:11434")
    tables = load_tables()

    print("Healthcare Demo Agent (LOCAL OLLAMA) running.")
    print("Commands:")
    print("- list tables")
    print("- show schema")
    print("- patients with ICD10 E11")
    print("- summary P001")
    print("- latest A1C for P001")
    print("- find patient Amy")
    print("Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()
        if user.lower() in {"exit", "quit"}:
            print("Bye!")
            return

        tool_name, tool_args = route_to_tool(user)
        if tool_name:
            result = run_tool(tables, tool_name, tool_args)
            print("\nAgent:", result, "\n")
        else:
            result = llm_answer(client, model, user)
            print("\nAgent:", result, "\n")


if __name__ == "__main__":
    main()
