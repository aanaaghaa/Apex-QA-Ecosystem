import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..state import QAState

def fetch_html_node(state: QAState) -> dict:
    """Fetches rendered HTML from the local Angular Practice Software Testing app."""
    url = state["target_url"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # Ensure Angular has rendered content inside app-root
        page.wait_for_selector("app-root *", timeout=10000)
        raw_html = page.content()
        browser.close()
        
    return {
        "raw_html": raw_html,
        "retry_count": 0,
        "audit_passed": False,
        "missing_elements": [],
        "audit_feedback": ""
    }

def compress_dom_node(state: QAState) -> dict:
    """
    Replace the body of this function with your existing compressor logic.
    Uses retry_count to relax stripping if the auditor flags dropped elements.
    """
    raw_html = state["raw_html"]
    retry_count = state.get("retry_count", 0)

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style", "svg", "path", "meta", "link", "noscript"]):
        tag.decompose()

    allowed_attrs = {
        "id", "name", "type", "placeholder", "href", 
        "role", "aria-label", "data-*", "for", "value"
    }
    if retry_count > 0:
        allowed_attrs.update({"class", "title", "alt", "disabled", "readonly"})

    for tag in soup.find_all(True):
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed_attrs}

    compressed = re.sub(r"\s+", " ", str(soup)).strip()

    return {
        "compressed_dom": compressed,
        "retry_count": retry_count + 1
    }

def audit_compression_node(state: QAState) -> dict:
    """Deterministic auditor verifying locators and interactive tags across all pages."""
    raw_soup = BeautifulSoup(state["raw_html"], "html.parser")
    comp_soup = BeautifulSoup(state["compressed_dom"], "html.parser")

    missing = []

    # 1. Check all data-*test attributes (used heavily across Toolshop pages)
    raw_datatests = {el.get("data-*") for el in raw_soup.find_all(attrs={"data-*": True})}
    comp_datatests = {el.get("data-*") for el in comp_soup.find_all(attrs={"data-*": True})}
    
    dropped_selectors = raw_datatests - comp_datatests
    if dropped_selectors:
        missing.append(f"Dropped data-*: {', '.join(sorted(dropped_selectors))}")

    # 2. Check interactive elements (includes <a> for product cards & nav links)
    for tag in ["input", "button", "select", "textarea", "a"]:
        raw_count = len(raw_soup.find_all(tag))
        comp_count = len(comp_soup.find_all(tag))
        if comp_count < raw_count:
            missing.append(f"Lost {raw_count - comp_count} <{tag}> elements")

    # 3. Check form IDs so <label for="..."> associations don't break on register/contact pages
    raw_ids = {el.get("id") for el in raw_soup.find_all(["input", "select", "textarea"], id=True)}
    comp_ids = {el.get("id") for el in comp_soup.find_all(["input", "select", "textarea"], id=True)}
    dropped_ids = raw_ids - comp_ids
    if dropped_ids:
        missing.append(f"Dropped form IDs: {', '.join(sorted(dropped_ids))}")

    audit_passed = len(missing) == 0
    feedback = "All interactive elements, links, and locators preserved." if audit_passed else "; ".join(missing)

    return {
        "audit_passed": audit_passed,
        "missing_elements": missing,
        "audit_feedback": feedback
    }
