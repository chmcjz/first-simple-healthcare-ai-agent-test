from __future__ import annotations

import re
from ollama import Client
import tools as T


def route_to_tool(user_text: str) -> tuple[str | None, dict]:
    """
    Simple rule-based routing:
    - list tables
    - show schema
    - patients with ICD10 E11
    - summary P001
    - latest A1C for P001
    - find patient Amy
    """
    text = user_text.strip()

    if re.fullmatch(r"list\s+tables", text, flags=re.I):
        return "list_tables", {}

    if re.fullmatch(r"show\s+schema", text, flags=re.I):
        return "show_schema", {}

    m = re.search(r"patients\s+with\s+icd10\s+([A-Z0-9.]+)", text, flags=re.I)
    if m:
        return "patients_by_icd10", {"icd10": m.group(1).upper()}

    m = re.search(r"\bsummary\s+(P\d+)\b", text, flags=re.I)
    if m:
        return "patient_summary", {"patient_id": m.group(1).upper()}

    m = re.search(r"latest\s+([A-Za-z0-9]+)\s+for\s+(P\d+)", text, flags=re.I)
    if m:
        test = m.group(1).upper()
        pid = m.group(2).upper()
        return "latest_lab", {"patient_id": pid, "test": test}

    m = re.search(r"find\s+patient\s+(.+)$", text, flags=re.I)
    if m:
        name_contains = m.group(1).strip()
        return "find_patient", {"name_contains": name_contains}

    return None, {}


def run_tool(tables, tool_name: str, tool_args: dict) -> str:
    if tool_name == "list_tables":
        return T.list_tables(tables)
    if tool_name == "show_schema":
        return T.show_schema(tables)
    if tool_name == "find_patient":
        return T.find_patient(tables, tool_args["name_contains"])
    if tool_name == "patients_by_icd10":
        return T.patients_by_icd10(tables, tool_args["icd10"])
    if tool_name == "latest_lab":
        return T.latest_lab(tables, tool_args["patient_id"], tool_args["test"])
    if tool_name == "patient_summary":
        return T.patient_summary(tables, tool_args["patient_id"])
    return f"Unknown tool: {tool_name}"


def llm_answer(client: Client, model: str, user_text: str) -> str:
    system = (
        "You are a healthcare data assistant for a SYNTHETIC demo dataset.\n"
        "You must NOT provide medical advice, diagnosis, or treatment.\n"
        "If the user asks for medical advice, refuse briefly and suggest asking a clinician.\n"
        "Otherwise, help them rephrase into one of these commands:\n"
        "- list tables\n"
        "- show schema\n"
        "- patients with ICD10 <CODE>\n"
        "- summary <PATIENT_ID>\n"
        "- latest <TEST> for <PATIENT_ID>\n"
        "- find patient <NAME>\n"
    )

    resp = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
    )
    return resp["message"]["content"]
