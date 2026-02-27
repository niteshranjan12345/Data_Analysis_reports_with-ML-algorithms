from medical_report_agent.agent import MedicalReportAgent


def test_extract_and_triage_urgent_case():
    report = """
    Patient Name: Alice Smith
    Age: 61
    Sex: Female
    Hemoglobin: 10.8 g/dL
    Fasting Glucose: 165 mg/dL
    Creatinine: 1.8 mg/dL
    LDL: 140 mg/dL
    """

    agent = MedicalReportAgent()
    result = agent.analyze_report(report)

    assert result.patient_name == "Alice Smith"
    assert result.age == 61
    assert result.sex == "Female"
    assert result.urgency == "urgent"
    assert len(result.abnormal_flags) >= 3


def test_routine_when_no_abnormalities():
    report = """
    Name: Bob Lee
    Age: 35
    Gender: Male
    Hemoglobin: 14.2 g/dL
    WBC: 7.1 x10^9/L
    Platelets: 210 K/uL
    Creatinine: 1.0 mg/dL
    """

    agent = MedicalReportAgent()
    result = agent.analyze_report(report)

    assert result.patient_name == "Bob Lee"
    assert result.urgency == "routine"
    assert result.abnormal_flags == []
