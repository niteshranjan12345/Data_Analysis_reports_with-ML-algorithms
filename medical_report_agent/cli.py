import argparse
import json
from dataclasses import asdict

from medical_report_agent.agent import MedicalReportAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze plain-text medical reports.")
    parser.add_argument("report_file", help="Path to a text file containing a medical report")
    args = parser.parse_args()

    with open(args.report_file, "r", encoding="utf-8") as f:
        report_text = f.read()

    agent = MedicalReportAgent()
    result = agent.analyze_report(report_text)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
