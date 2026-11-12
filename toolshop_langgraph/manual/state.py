from typing import TypedDict, Optional, List

class QAState(TypedDict):
    target_url: str
    raw_html: Optional[str]
    compressed_dom: Optional[str]
    audit_passed: bool
    missing_elements: List[str]
    audit_feedback: str
    retry_count: int

    pom_code: Optional[str]
    test_code: Optional[str]

    feature_source: Optional[str]      # File path (e.g. 'features/login.feature') OR Jira key (e.g. 'QA-101')
    raw_requirements: Optional[str]    # Loaded Gherkin / Jira acceptance criteria
    expanded_scenarios: Optional[str]
