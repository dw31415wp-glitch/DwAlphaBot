
from pywikibot import Link, Page

from find_rfc import RfcStats
from config import site


def draft_report(results: list[tuple[RfcStats, str, Link]]) -> str:
    """Draft a report based on the collected RFC stats."""
    report_lines = ["=== RFC Analysis Report ===", "Very preliminary code and unaudited results.", ""]
    table_headers = """
        |-
        ! User 
        ! Number of edits to RFC 
        ! Total bytes of changes 
        |-"""
    for stats, rfc_id, link in results:
        report_lines.append("""{| class="wikitable" """)
        report_lines.append(f"|+ RFC stats: {str(link)}")             
        report_lines.append(table_headers)
        for user, stats in stats.user_counts.items():
            count, length = stats
            report_lines.append(f"|-\n | {user}\n | {count} \n| {length} \n")
        report_lines.append("|}") # close table  
        report_lines.append("\n")  # Blank line between RFCs
    return "\n".join(report_lines)

def publish_report(report: str, page_title: str) -> None:
    """Publish the report to the specified wiki page."""
    

    result_page = Page(site, str(page_title))

    results_exist = result_page.exists()
    print(f"Result page ({page_title}) exists: {results_exist}")

    
    print(f"Current content of result page ({page_title}):")
    print(result_page.text)

    result_page.text = report
    result_page.save(summary="Updating RFC analysis report", minor=False)
