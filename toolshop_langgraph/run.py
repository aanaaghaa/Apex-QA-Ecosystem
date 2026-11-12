from manual.graph import qa_graph
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

PAGES = [
    "http://localhost:4200/",
    "http://localhost:4200/auth/login",
    "http://localhost:4200/auth/register",
    "http://localhost:4200/contact",
    "http://localhost:4200/category/hand-tools",
    "http://localhost:4200/product/1",
    "http://localhost:4200/rentals"
]

def get_page_slug(url: str) -> str:
    """Converts URL path into a clean filename (e.g., '/auth/login' -> 'auth_login')."""
    path = urlparse(url).path.strip("/")
    return path.replace("/", "_").replace("-", "_") if path else "home"


if __name__ == "__main__":
    os.makedirs("compressed_html", exist_ok=True)
    for idx, target_url in enumerate(PAGES):
        slug = get_page_slug(target_url)
        config = {"configurable": {"thread_id": f"page-run-{slug}"}}
        result = qa_graph.invoke({"target_url": target_url,
                                 "retry_count": 0,
                                 "audit_passed": False,
                                "missing_elements": [],
                                "audit_feedback": ""}, 
                                config=config)

        raw_len = len(result["raw_html"])
        comp_len = len(result["compressed_dom"])
        reduction = ((raw_len - comp_len) / raw_len) * 100 if raw_len else 0

        print("=" * 50)
        print(f"Page: {target_url} ({slug}.html)")
        print(f"  Raw: {raw_len:,} -> {comp_len:,} chars -> Compressed: {comp_len:,} chars ({reduction:.1f}% reduction)\n")
        print("=== AUDIT REPORT ===")
        print(f"Audit Passed   : {result['audit_passed']}")
        print(f"Attempts Used  : {result.get('retry_count', 1)}")
        print(f"Feedback       : {result['audit_feedback']}")

        if result["missing_elements"]:
            print("Missing Items  :")
            for item in result["missing_elements"]:
                print(f"  - {item}")


        # Pretty-print so it's easy to read in Cursor
        pretty_html = BeautifulSoup(result["compressed_dom"], "html.parser").prettify()
        with open(f"compressed_html/page_{slug}.html", "w", encoding="utf-8") as f:
            f.write(pretty_html)
