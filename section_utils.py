
import mwparserfromhell


def get_comments_from_section_text(text: str) -> list[dict[str, str]]:
    """Extract sections from wikitext using mwparserfromhell.
    
    Returns a list of dicts with 'heading' and 'text' keys.
    """
    wikicode = mwparserfromhell.parse(text)
    
    # use filter_comments to get comments
    nodes = wikicode.nodes
    for node in nodes:
        print('Node type:', type(node))
        print('Node content:', str(node)[:100], '...')
        lines = node.splitlines()
        for line in lines:
            print('  Line:', line)

if __name__ == "__main__":
    from pathlib import Path
    
    sample_text = ""
    rfc_file = Path("rfc_section.txt")
    with rfc_file.open("r") as f:
        sample_text = f.read()
    
    sections = get_comments_from_section_text(sample_text)
    for sec in sections:
        print(f"Heading: {sec['heading']}\nText: {sec['text'][:100]}...\n---\n")