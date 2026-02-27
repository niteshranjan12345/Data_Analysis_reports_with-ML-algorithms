from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class LabResult:
    name: str
    value: float
    unit: str
    reference_range: Optional[Tuple[float, float]] = None


@dataclass
class MedicalReportAnalysis:
    patient_name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    labs: List[LabResult] = field(default_factory=list)
    abnormal_flags: List[str] = field(default_factory=list)
    urgency: str = "routine"
    summary: str = ""


class MedicalReportAgent:
    """A lightweight AI-style agent for analyzing plain-text medical reports.

    The agent extracts demographic details, lab values, compares values against
    built-in normal ranges, and generates a triage summary.
    """

    # Conservative generic adult reference ranges.
    DEFAULT_RANGES: Dict[str, Tuple[float, float]] = {
        "hemoglobin": (12.0, 17.5),
        "wbc": (4.0, 11.0),
        "platelets": (150.0, 450.0),
        "glucose_fasting": (70.0, 99.0),
        "hba1c": (4.0, 5.6),
        "creatinine": (0.6, 1.3),
        "alt": (7.0, 56.0),
        "ast": (10.0, 40.0),
        "ldl": (0.0, 100.0),
        "hdl": (40.0, 100.0),
        "triglycerides": (0.0, 150.0),
    }

    FIELD_ALIASES: Dict[str, str] = {
        "hb": "hemoglobin",
        "hemoglobin": "hemoglobin",
        "white blood cell": "wbc",
        "wbc": "wbc",
        "platelet": "platelets",
        "platelets": "platelets",
        "fasting glucose": "glucose_fasting",
        "glucose fasting": "glucose_fasting",
        "hba1c": "hba1c",
        "creatinine": "creatinine",
        "alt": "alt",
        "ast": "ast",
        "ldl": "ldl",
        "hdl": "hdl",
        "triglycerides": "triglycerides",
    }

    def analyze_report(self, report_text: str) -> MedicalReportAnalysis:
        patient_name = self._extract_name(report_text)
        age = self._extract_age(report_text)
        sex = self._extract_sex(report_text)
        labs = self._extract_labs(report_text)

        abnormal_flags = self._detect_abnormal(labs)
        urgency = self._assign_urgency(abnormal_flags)
        summary = self._build_summary(patient_name, abnormal_flags, urgency)

        return MedicalReportAnalysis(
            patient_name=patient_name,
            age=age,
            sex=sex,
            labs=labs,
            abnormal_flags=abnormal_flags,
            urgency=urgency,
            summary=summary,
        )

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [r"(?:Patient Name|Name)\s*[:\-]\s*([A-Za-z .']+)", r"Patient\s*[:\-]\s*([A-Za-z .']+)"]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_age(self, text: str) -> Optional[int]:
        match = re.search(r"(?:Age)\s*[:\-]\s*(\d{1,3})", text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    def _extract_sex(self, text: str) -> Optional[str]:
        match = re.search(r"(?:Sex|Gender)\s*[:\-]\s*(Male|Female|Other)", text, flags=re.IGNORECASE)
        return match.group(1).capitalize() if match else None

    def _extract_labs(self, text: str) -> List[LabResult]:
        results: List[LabResult] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            m = re.search(r"^([A-Za-z0-9 _\-/()]+?)\s*[:\-]\s*([0-9]+(?:\.[0-9]+)?)\s*([%A-Za-z/µ]+)?", line)
            if not m:
                continue
            raw_name, raw_value, raw_unit = m.groups()
            normalized = self._normalize_lab_name(raw_name)
            if not normalized:
                continue
            value = float(raw_value)
            unit = (raw_unit or "").strip()
            ref = self.DEFAULT_RANGES.get(normalized)
            results.append(LabResult(name=normalized, value=value, unit=unit, reference_range=ref))
        return results

    def _normalize_lab_name(self, raw: str) -> Optional[str]:
        key = re.sub(r"\s+", " ", raw.lower()).strip()
        for alias, canonical in self.FIELD_ALIASES.items():
            if alias in key:
                return canonical
        return None

    def _detect_abnormal(self, labs: List[LabResult]) -> List[str]:
        flags: List[str] = []
        for lab in labs:
            if not lab.reference_range:
                continue
            low, high = lab.reference_range
            if lab.value < low:
                flags.append(f"{lab.name} low ({lab.value})")
            elif lab.value > high:
                flags.append(f"{lab.name} high ({lab.value})")
        return flags

    def _assign_urgency(self, flags: List[str]) -> str:
        if not flags:
            return "routine"

        critical_markers = ["glucose_fasting", "creatinine", "platelets", "hemoglobin"]
        severe = sum(1 for flag in flags if any(marker in flag for marker in critical_markers))

        if severe >= 2 or len(flags) >= 4:
            return "urgent"
        if severe == 1 or len(flags) >= 2:
            return "priority"
        return "routine"

    def _build_summary(self, patient_name: Optional[str], flags: List[str], urgency: str) -> str:
        subject = patient_name or "The patient"
        if not flags:
            return f"{subject} has no obvious out-of-range markers from extracted labs. Suggested follow-up: routine review."

        findings = "; ".join(flags)
        return (
            f"{subject} has {len(flags)} out-of-range findings: {findings}. "
            f"Recommended triage level: {urgency}. "
            "Clinical correlation and physician review are required before any diagnosis."
        )
