# Data_Analysis_reports_with-ML-algorithms

## Medical Report AI Agent

This repository now includes a lightweight AI-style medical report analyzer that can:
- Parse plain-text medical reports.
- Extract patient details (name, age, sex).
- Extract common lab values.
- Flag out-of-range lab markers with simple rule-based triage (`routine`, `priority`, `urgent`).

> **Important**: This tool is for report summarization support only and is **not** a medical diagnosis system.

### Files
- `medical_report_agent/agent.py` — core analysis logic.
- `medical_report_agent/cli.py` — command-line interface.
- `sample_medical_report.txt` — sample report for testing.

### Usage

```bash
python -m medical_report_agent.cli sample_medical_report.txt
```

### Example output (shortened)

```json
{
  "patient_name": "John Doe",
  "age": 52,
  "sex": "Male",
  "urgency": "urgent",
  "summary": "John Doe has ..."
}
```
