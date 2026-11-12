from bs4 import BeautifulSoup, Comment
from ..state import QAState
from playwright.sync_api import sync_playwright


ALLOWED_ATTRS={
    #Automation
    "id", "name", "type", "placeholder","href", "role","aria-label","for", "value","data-*", "class",
    #Manual
    "required","minlength","maxlength","pattern", "disabled"
    }
NOISY_TAGS=["script", "style", "svg", "noscript", "meta", "link", "iframe", "path", "g"]

def fetch_html_node(state: QAState) -> dict:
     """Renders the Angular SPA via Playwright and captures the live DOM."""
     with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        page.goto(state["target_url"], wait_until="networkidle", timeout=15000)

        page.evaluate("""() => {
                document.querySelectorAll('svg').forEach(el => el.remove());
            }""")

        raw_html=page.content()
        browser.close()

     return{"raw_html":raw_html}

def compress_dom_node(state: QAState) -> dict:
    """Deterministically compresses raw HTML without an LLM while preserving QA context."""
    soup = BeautifulSoup(state["raw_html"], "html.parser")

    # Removing noisy tags
    for tag in soup(NOISY_TAGS):
        tag.decompose()

        #Stripping non-essentials attribs and keeping QA and validation attributes
        for tag in soup.find_all(True):
            cleaned_attrs = {}
            for attr, val in tag.attrs.items():
                if attr in ALLOWED_ATTRS or attr.startswith("data-test"):
                    if attr=="class" and isinstance(val, list):
                        cleaned_attrs[attr] = " ".join(val[:3])
                    else:
                        cleaned_attrs[attr]=val
                tag.attrs=cleaned_attrs


        #Unwrap the empty structural wrappers without deleting child elements                        
        for tag in soup.find_all(["div", "span"]):
            has_direct_text=any(isinstance(child,str) and child.strip() for child in tag.contents)
            if not tag.attrs and not has_direct_text:
                tag.unwrap()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        #Collapse extra whitespace into a clean, token-efficient string
        compressed=" ".join(str(soup.body or soup).split())
        return {"compressed_dom": compressed,
                  "retry_count": state.get("retry_count", 0) + 1}        