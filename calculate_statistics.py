
import mwparserfromhell

def contains_datetime(text: str) -> bool:
    """Check if the text contains a datetime pattern."""
    import re
    datetime_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
    # 01:02, 30 December 2025 (UTC)
    datetime_pattern += r'|\d{2}:\d{2}, \d{1,2} [A-Za-z]+ \d{4} \(UTC\)'
    return re.search(datetime_pattern, text) is not None

def calculate_statistics(rfc_section: mwparserfromhell.wikicode.Wikicode) -> dict[str, tuple[int, int]]:
    """Calculate user mention statistics from the RFC section."""
    user_counts: dict[str, int] = {}
    user_lengths: dict[str, int] = {}
    user_statistics: dict[str, tuple[int, int]] = {}
    previous_lenth = 0
    previous_node = None
    current_node = rfc_section.nodes[0] if rfc_section.nodes else None
    unknown_author_nodes = []
    for node in rfc_section.nodes:
        current_node = node
        print('Node type:', type(node))
        print('Node content:', str(node)[:100], '...')
        is_datetime = False
        if type(node) == mwparserfromhell.nodes.Text:
            is_datetime = contains_datetime(str(node))
        if is_datetime:
            if previous_node is not None:
                # is the previous node a wikilink to a user talk page?
                if type(previous_node) == mwparserfromhell.nodes.Wikilink:
                    link_target = str(previous_node.title).strip()
                    if link_target.startswith("User talk:"):
                        username = link_target[10:].split("|")[0].strip()
                        if username:
                            user_counts[username] = user_counts.get(username, 0) + 1
                            user_lengths[username] = user_lengths.get(username, 0) + previous_lenth
                            user_statistics[username] = (user_counts[username], user_lengths[username])
                            previous_lenth = len(str(current_node)) # ignore length of datetime
                    else:
                        unknown_author_nodes.append(previous_node)
                author_text = str(previous_node).strip()
        else:
            previous_lenth += len(str(node))
        
        previous_node = current_node

    return user_statistics

if __name__ == "__main__":
    from pathlib import Path
    
    sample_text = ""
    rfc_file = Path("rfc_section.txt")
    with rfc_file.open("r") as f:
        sample_text = f.read()
    
    wikicode = mwparserfromhell.parse(sample_text)
    stats = calculate_statistics(wikicode)
    print("User mention statistics:")
    for user, count in stats.items():
        print(f"{user}: {count}")