# First Simple Healthcare AI Agent (Local, Free)

A tiny command-line “AI agent” that answers questions about a **synthetic** healthcare dataset (CSV).
Runs **100% locally** using **Ollama** (no OpenAI API key, no paid API).

## Demo commands
- `list tables`
- `show schema`
- `patients with ICD10 E11`
- `summary P001`
- `latest A1C for P001`
- `find patient Amy`

## Setup (Windows PowerShell)

### 1) Install Ollama and pull a model
```powershell
ollama --version
ollama pull llama3.1
