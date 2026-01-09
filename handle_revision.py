
from datetime import datetime
from pydoc import text
import re
import mwparserfromhell
from pywikibot.time  import Timestamp
from pywikibot import textlib
from config import site

from pywikibot.diff import html_comparator

page_shortcuts = {}

printed_links = {}



def find_shortcut(page_title: str) -> str:
    """
    Given a page title, find the shortcut key from RAW_PAGES_DICT.

    Args:
        page_title (str): The full page title.
    Returns:
        str: The shortcut key if found, else full page title.
    """
    if not page_shortcuts:
        from config import RAW_PAGES_DICT
        for shortcut, title in RAW_PAGES_DICT.items():
            full_title = f"Wikipedia:{title}"
            page_shortcuts[full_title] = shortcut

    return page_shortcuts.get(page_title, page_title)    

comment_keywords = ['added','removed', 'deleted', 'maintenance']

def extract_revisions(diff_entries: list[dict]) -> list[dict]:
    """
    Given a list of diff entries, extract revision information.

    Args:
        diff_entries (list[dict]): List of diff entries.
    Returns:
        list[dict]: List of revisions extracted.
    """
    revisions_by_shortcut = {}
    revisions = []
    for entry in diff_entries:
        revision_id = entry.get('revid')
        page_title = entry.get('page_title')
        comment = entry.get('comment', '').lower()
        # extract key words added, maintenance, removed from comment    
        keywords_found = [kw for kw in comment_keywords if kw in comment]
        revision = {
            'revid': revision_id,
            'page_title': page_title,
            'comment_kw': ", ".join(keywords_found),
            'shortcut': find_shortcut(page_title),
            'timestamp': entry.get('timestamp')
        }
        if page_title and revision_id:
            label = f"{find_shortcut(page_title)} {revision_id}"
            diff_template = "{{" + f"Diff|{page_title}|prev|{revision_id}|{label}" + "}}"
            revision['diff_template'] = diff_template
        revisions.append(revision)
        shortcut = revision['shortcut']
        if shortcut not in revisions_by_shortcut:
            revisions_by_shortcut[shortcut] = []
        revisions_by_shortcut[shortcut].append(revision)

    # sort each shortcut's revisions by timestamp ascending
    for revs in revisions_by_shortcut.values():
        revs.sort(key=lambda x: x.get('timestamp'))

    # find first and last revision by shortcut
    for revs in revisions_by_shortcut.values():
        if revs:
            first_rev = revs[0]
            last_rev = revs[-1]
            
    first_and_last_revs = []

    for revs in revisions_by_shortcut.values():
        if revs:
            first_rev = revs[0]
            last_rev = revs[-1]
            first_and_last_revs.append(first_rev)
            if last_rev != first_rev:
                first_and_last_revs.append(last_rev)

    # sort first_and_last_revs by timestamp ascending
    first_and_last_revs.sort(key=lambda x: x.get('timestamp'))

    return first_and_last_revs

def file_appender(entry: dict, rfcs: dict[str, dict], rfc_id_dict: dict[str, dict], file_names: dict):
    """
    Append text to a file.

    Args:
        filename (str): The name of the file to append to.
        text (str): The text to append.
    """

    # find shortcut for page title
    entry_page_title = entry.get('page_title', '')
    shortcut = find_shortcut(entry_page_title)


    year = entry.get('year')
    filename = f"./logs/removed_rfcs_{year}.txt"
    error_filename = f"./logs/removed_rfcs_errors_{year}.txt"
    file_names[year] = {filename, error_filename}

    # if rfcs is empty, log to error file
    if not rfcs:
        with open(error_filename, 'a', encoding='utf-8') as f:
            f.write(f"== No RFCs found for revision {entry.get('revid')} ==\n")
            f.write(f"Entry details: {entry}\n\n")
        return
    

    if rfcs:
        with open(filename, 'a', encoding='utf-8') as f:
            timestamp: Timestamp = entry.get('timestamp')
            if timestamp:
                # get YYYY-MM-DD HH:MM format
                timestamp_str = f"expired {timestamp.year}-{timestamp.month:02}-{timestamp.day:02} {timestamp.hour:02}:{timestamp.minute:02}"
            else:
                timestamp_str = ''

            #f.write(f"== Removed RFC from {shortcut} {entry.get('revid')} {timestamp_str}  ==\n")
            for rfc in rfcs.values():                
                link = rfc.get('link', '')
                rfc_id = rfc.get('rfc_id', '')
                diff_entries = rfc_id_dict.get(rfc_id, {}).get('diff_entries', [])
                revisions = extract_revisions(diff_entries)

                # only print the following if not seen before in printed_links
                if rfc.get('link') not in printed_links:
                    header = f"=== {link} {timestamp_str} ===\n" if link else f"== Removed RFC from {shortcut} {entry.get('revid')} {timestamp_str}  ==\n"
                    f.write(f"{header}")
                    printed_links[rfc.get('link')] = shortcut
                    f.write(f"* Id: {rfc_id}\n")
                    if rfc.get('user'):
                        f.write(f"* User: {rfc.get('user')}\n")
                    if rfc.get('datetime'):
                        f.write(f"* Date: {rfc.get('datetime')}\n")
                    if revisions:
                        f.write("* Revisions affecting this RFC:\n")
                        for rev in revisions:
                            f.write(f"** {rev.get('diff_template')}\n")
                    if rfc.get('rfc_text'):
                        f.write(f"* RFC Text:\n{rfc.get('rfc_text')}\n\n")


def extract_user_and_date(rfc_text: str) -> tuple[str, Timestamp]:
    """
    Given a block of text from an RFC entry, attempt to find the user who made the entry and the date.

    Args:
        rfc_text (str): The block of text containing the RFC entry. 
    Returns:
        tuple[str, Timestamp]: A tuple containing the username and the timestamp of the entry.
    """

    user = None
    rfc_datetime = None

    # date will be like  05:33, 24 December 2020 (UTC)}}
    date_re = r'(\d{2}:\d{2}, \d{1,2} \w+ \d{4} \(UTC\)\}\})'
    user_talk_re = r'\[\[User talk:(.+?)\|'
    # contrib like [[Special:Contributions/Username|my edits]]
    user_contrib_re = r'\[\[Special:Contributions/(.+?)\|'

    import re
    date_match = re.search(date_re, rfc_text)
    user_match = re.search(user_talk_re, rfc_text)
    contrib_match = re.search(user_contrib_re, rfc_text)


    try:
        if date_match:
            date_str = date_match.group(1).replace(' (UTC)}}', '')
            # for a string like '05:33, 24 December 2020'
            # convert to Timestamp by constructing a datetime object
            rfc_datetime = datetime.strptime(date_str, '%H:%M, %d %B %Y')
        if user_match:
            user = user_match.group(1)
        elif contrib_match:
            user = contrib_match.group(1)
    except Exception as e:
        print(f"Error extracting user/date from RFC text: {rfc_text[:100]} {e.__class__.__name__}: {e}")

    return (user, rfc_datetime)

def print_removed_entries(entry, print_keys, diff_table=None, rfc_id_dict=None, file_names=None):
    rfcs: dict[str, dict] = {}
    diff_compare = html_comparator(diff_table)

    deleted_content = diff_compare['deleted-context'] or []
    deleted_lines = '\n'.join(deleted_content)

    link_re, header_re, template_re = textlib.get_regexes(['link', 'header', 'template'], site)
    rfc_start_pos = []

    rfc_links = []
    for m in link_re.finditer(deleted_lines):
        group = m.group(0)
        print('link match:', group)
        if "#rfc_" in group.lower():
            print("Found RFC link in deleted lines:", group)
            start, end = m.span(0)
            rfc_start_pos.append(start)
            rfcs[group] = {"link": group, "link_start": start, "link_end": end}
            rfc_links.append(group)

    # divide text by start positions

    number_of_rfcs = len(rfc_start_pos)
    rfc_texts = []
    for i in range(number_of_rfcs):
        start = rfc_start_pos[i]
        if i < number_of_rfcs - 1:
            end = rfc_start_pos[i + 1]
            rfc_text = deleted_lines[start:end]
        else:
            rfc_text = deleted_lines[start:]
        rfc_texts.append(rfc_text)
        # associate rfc_text with corresponding rfc in rfcs
        link = rfc_links[i]
        # extract user and date
        user, rfc_datetime = extract_user_and_date(rfc_text)
        # extract rfc_id from link
        rfc_id_match = re.search(r'#rfc_([a-zA-Z0-9]+)', link)
        if rfc_id_match:
            rfc_id = rfc_id_match.group(1)
            rfcs[link]['rfc_id'] = rfc_id
        if user:
            rfcs[link]['user'] = user
        if rfc_datetime:
            rfcs[link]['datetime'] = rfc_datetime
        # remove link from rfc_text to avoid repetition in output
        rfc_text = rfc_text.replace(link, '', 1)
        # trim - Trim ''' from start and end of rfc_text
        rfc_text = rfc_text.strip().strip("'''")
        rfcs[link]['rfc_text'] = rfc_text


    # find case where no rfc_links found
    # if not rfc_links:
    #     print("No RFC links found in deleted lines.")
    #     pass

    # find rfc_link but no rfc_texts


    file_appender(entry, rfcs, rfc_id_dict)

    # print(f'== Removed RFC Entries ==')
    # for rfc_text in rfc_texts:
    #     user, rfc_datetime = extract_user_and_date(rfc_text)
    #     print(f"RFC Text:\n{rfc_text}\nUser: {user}, Date: {rfc_datetime}\n")




def print_removed_entries2(entry, print_keys, diff_table=None):
    rfcs: dict[str, dict] = {}
    comment = entry.get('comment')
            # Delete everything before "[["
    if "[[" in comment:
        comment = comment[comment.index("[["):]
            # remove any trailing period
    if comment.endswith('.'):
        comment = comment[:-1]

    print(f'== {comment} ==')
    revision_comment = '<!-- dwalphabot=1,'
    for key in print_keys:
                #print(f"* {key}: {entry.get(key)}")
        revision_comment += f"{key}={str(entry.get(key))},"
    revision_comment += ' -->\n'
    print(revision_comment)
    # diff_table = site.compare(entry.get('parentid'), entry.get('revid'),'table') # works better than 'inline'
    diff_compare = html_comparator(diff_table)

    deleted_content = diff_compare['deleted-context'] or []
    deleted_lines = '\n'.join(deleted_content)

    wikicode = mwparserfromhell.parse(deleted_lines)

    for node in wikicode.nodes:
        print(f"Node: {node.__class__.__name__}: {str(node)}")

    for template in wikicode.filter_templates():
        print('template match:', str(template))

    link_re, header_re, template_re = textlib.get_regexes(['link', 'header', 'template'], site)

    rfc_start_pos = []

    for m in link_re.finditer(deleted_lines):
        group = m.group(0)
        print('link match:', group)
        if "#rfc_" in group.lower():
            print("Found RFC link in deleted lines:", group)
            start, end = m.span(0)
            rfc_start_pos.append(start)
            rfcs[group] = {"link": group, "start": start, "end": end}

    for m in header_re.finditer(deleted_lines):
        print('header match:', m.group(0))


    for m in template_re.finditer(deleted_lines):
        print('template match:', m.group(0))

    # print(deleted_lines)
    print("")

    # if multiple RFC found, divide text accordingly
    if len(rfc_start_pos) > 1:
        number_of_rfcs = len(rfc_start_pos)
        for i in range(number_of_rfcs):
            rfc = list(rfcs.values())[i]
            start = rfc['start']
            end = rfc['end']
            if i < number_of_rfcs - 1:
                next_rfc = list(rfcs.values())[i + 1]
                next_start = next_rfc['start']
                rfc_text = deleted_lines[start:next_start]
                # if rfc_text ends with ''', remove it
                if rfc_text.endswith("'''"):
                    rfc_text = rfc_text[:-3]
                rfc['rfc_text'] = rfc_text
            else:
                rfc_text = deleted_lines[start:]
                # if rfc_text ends with ''', remove it
                if rfc_text.endswith("'''"):
                    rfc_text = rfc_text[:-3]
                rfc['rfc_text'] = rfc_text
            user, rfc_datetime = extract_user_and_date(rfc_text)
            rfc['user'] = user
            rfc['datetime'] = rfc_datetime
            print(f"RFC Text for {rfc['link']}:\n{rfc_text}\n")
    else:
        for rfc in rfcs.values():
            rfc_text = deleted_lines[rfc['start']:]
            # if rfc_text ends with ''', remove it
            if rfc_text.endswith("'''"):
                rfc_text = rfc_text[:-3]
            rfc['rfc_text'] = rfc_text
            user, rfc_datetime = extract_user_and_date(rfc_text)
            rfc['user'] = user
            rfc['datetime'] = rfc_datetime
            print(f"RFC Text for {rfc['link']}:\n{rfc_text}\n")

    for rfc in rfcs.values():
            # remove link from rfc_text to avoid repetition in output
            link = rfc['link']
            rfc_text = rfc_text.replace(link, '', 1)
            rfc['rfc_text'] = rfc_text

        # Find special case where there are two "#rfc_" in the deleted lines
    if deleted_lines.count('#rfc_') > 1:
        pass




def handle_revision(entry: dict, rfc_id_dict: dict, file_names: dict):
    print_keys = ['revid', 'parentid', 'timestamp', 'user', 'comment']
    if 'removed' in entry.get('comment', '').lower():
        print_removed_entries(entry, print_keys, entry.get('diff_table'), rfc_id_dict, file_names)

if __name__ == "__main__":
    #entry = {'revid': 1063078964, 'parentid': 1062709000, 'timestamp': Timestamp(2022, 1, 1, 3, 1, 22), 'user': 'Legobot', 'comment': 'Removed: [[Wikipedia talk:Notability (organizations and companies)]].', 'diff_table': '<tr>\n  <td colspan="2" class="diff-lineno">Line 55:</td>\n  <td colspan="2" class="diff-lineno">Line 55:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>(Editors {{u|Binksternet}}, {{u|Black Kite}}, {{u|FormalDude}} expressed opinions above). &lt;s&gt;Also, @ {{u|CAMERAwMUSTACHE}}, {{u|ChicagoWikiEditor}}, {{u|FMSky}} if they have time for suggestions, would be welcome&lt;/s&gt;.</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>(Editors {{u|Binksternet}}, {{u|Black Kite}}, {{u|FormalDude}} expressed opinions above). &lt;s&gt;Also, @ {{u|CAMERAwMUSTACHE}}, {{u|ChicagoWikiEditor}}, {{u|FMSky}} if they have time for suggestions, would be welcome&lt;/s&gt;.</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>[[User:Cornerstonepicker|Cornerstonepicker]] ([[User talk:Cornerstonepicker|talk]]) 02:13, 3 December 2021 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>[[User:Cornerstonepicker|Cornerstonepicker]] ([[User talk:Cornerstonepicker|talk]]) 02:13, 3 December 2021 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Wikipedia talk:Notability (organizations and companies)#rfc_4ED494F|Wikipedia talk:Notability (organizations and companies)]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the line {{tq|The scope of this guideline covers all groups of people organized together for a purpose with the exception of non-profit educational institutions, religions or sects, and sports teams.}} be altered to state:</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'A\'\'\': That esports are within the scope of this notability guideline</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'B\'\'\': That esports are not within the scope of this notability guideline</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'C\'\'\': No change</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><br /></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>This RfC is proposed in the context of the no consensus [[Wikipedia:Articles for deletion/Stalwart Esports (2nd nomination)|Stalwart Esports AfD]] where the closer opined that there was a "real need" for guidance on which guideline or policy was controlling.</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>02:32, 2 December 2021 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{RFC list footer|bio|hide_instructions={{{hide_instructions}}} }}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{RFC list footer|bio|hide_instructions={{{hide_instructions}}} }}</div></td>\n</tr>\n', 'page_title': 'Wikipedia:Requests_for_comment/Biographies', 'year': 2022}
    user_exception_entry = {'revid': 576752293, 'parentid': 576088456, 'timestamp': Timestamp(2013, 10, 11, 18, 1, 40), 'user': 'Legobot', 'comment': 'Removed: [[Wikipedia:Requests for comment/Template editor user right]].', 'diff_table': '<tr>\n  <td colspan="2" class="diff-lineno">Line 195:</td>\n  <td colspan="2" class="di...{hide_instructions}}} }}</div></td>\n</tr>\n', 'page_title': 'Wikipedia:Requests_for_comment/Wikipedia_technical_issues_and_templates', 'year': 2013}
    entry = {'revid': 1000204955, 'parentid': 1000195870, 'timestamp': Timestamp(2021, 1, 14, 3, 1, 30), 'user': 'Legobot', 'comment': 'Removed: [[Talk:Arthur Laffer]] [[Talk:Ted Cruz]] [[Talk:Emily VanDerWerff]].', 'diff_table': '<tr>\n  <td colspan="2" class="diff-lineno">Line 21:</td>\n  <td colspan="2" class="diff-lineno">Line 21:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>Here we go again. [[User:Artixxxl|Artixxxl]] is adding to the list people who are not Ukrainian citizens, who were not born in Ukraine (or area which is now Ukraine) and never lived there, on the nasis that they have Ukrainian ancestry (one example of [[Alexei Navalny]] spending summers with his grandparents - which I personally find completely ridiculous; in this way everybody who was on holidays in Crimea between 1954 and 2014 - or even possibly after 2014 - can be added to the list) and this would make the list potentially of infinite size - even I would qualify for inclison. Therefore we need to define the scope very clearly. Below I list categories of notable individuals, please argue whether these need to be included.--[[User:Ymblanter|Ymblanter]] ([[User talk:Ymblanter|talk]]) 10:06, 1 January 2021 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>Here we go again. [[User:Artixxxl|Artixxxl]] is adding to the list people who are not Ukrainian citizens, who were not born in Ukraine (or area which is now Ukraine) and never lived there, on the nasis that they have Ukrainian ancestry (one example of [[Alexei Navalny]] spending summers with his grandparents - which I personally find completely ridiculous; in this way everybody who was on holidays in Crimea between 1954 and 2014 - or even possibly after 2014 - can be added to the list) and this would make the list potentially of infinite size - even I would qualify for inclison. Therefore we need to define the scope very clearly. Below I list categories of notable individuals, please argue whether these need to be included.--[[User:Ymblanter|Ymblanter]] ([[User talk:Ymblanter|talk]]) 10:06, 1 January 2021 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Ted Cruz#rfc_76C58B0|Talk:Ted Cruz]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the lead section conclude with one sentence about his family (being that two of his family members meet the Wikipedia criteria of notability itself by having articles), just like most large biographies of living persons typically do, in a neutral manner and without giving an inference of perceived "inherited notability" and / or granting notability to the subject? Or is it really against a policy and does the one sentence make the article about them? I’m here to get consensus as I allegedly didn’t do that by including something I assumed to be a non-issue in its ubiquity. And that I’ve seen nothing in the Manual of Style explicitly against it. [[User:Trillfendi|Trillfendi]] ([[User talk:Trillfendi|talk]]) 22:23, 29 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Emily VanDerWerff#rfc_C9A3824|Talk:Emily VanDerWerff]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the article include the subject\'s previous name in the opening paragraph? This has been omitted citing [[WP:DEADNAME]] because a previous version of this article was deleted. Does the fact that a previous version was deleted prove that the subject was not notable at the time? If so, does this proof satisfy [[WP:DEADNAME]], specifically that {{tq|the birth name should be included in the lead sentence only if the person was notable under that name}}?</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><br /></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Previous discussion of this question starts [https://en.wikipedia.org/wiki/Talk:Emily_VanDerWerff#Birth_name above]. [https://en.wikipedia.org/w/index.php?title=Emily_VanDerWerff&amp;oldid=996643305 Here] is a revision showing how it might appear. \'\'\'[[User:Careless hx|carelesshx]]\'\'\' &lt;sub&gt;[[User talk:Careless hx|talk]]&lt;/sub&gt; 16:04, 28 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>\'\'\'[[Talk:Donald Gary Young#rfc_F9665B6|Talk:Donald Gary Young]]\'\'\'</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>\'\'\'[[Talk:Donald Gary Young#rfc_F9665B6|Talk:Donald Gary Young]]\'\'\'</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td colspan="2" class="diff-lineno">Line 44:</td>\n  <td colspan="2" class="diff-lineno">Line 36:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>Should the lead note that Black wrote a "flattering biography of Donald Trump" and that he was pardoned \'\'by President Trump\'\'? Currently, the lead says Black was pardoned but it doesn\'t say by whom, and it doesn\'t include the context that Black had just prior to the pardon released a hagiography of Trump. (Original timestamp: 12:55, 13 May 2020) [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:35, 24 December 2020 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>Should the lead note that Black wrote a "flattering biography of Donald Trump" and that he was pardoned \'\'by President Trump\'\'? Currently, the lead says Black was pardoned but it doesn\'t say by whom, and it doesn\'t include the context that Black had just prior to the pardon released a hagiography of Trump. (Original timestamp: 12:55, 13 May 2020) [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:35, 24 December 2020 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Arthur Laffer#rfc_1AAC44C|Talk:Arthur Laffer]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should we add a paragraph to the article that mentions: (i) that Laffer is advising the trump administration on dealing with the coronavirus, and (ii) the policies that Laffer has advocated for in dealing with the coronavirus pandemic? [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:33, 24 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>\'\'\'[[Talk:Arthur Laffer#rfc_6BDAC22|Talk:Arthur Laffer]]\'\'\'</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>\'\'\'[[Talk:Arthur Laffer#rfc_6BDAC22|Talk:Arthur Laffer]]\'\'\'</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n', 'page_title': 'Wikipedia:Requests_for_comment/Biographies', 'year': 2021}
    print(f"Handling revision: {entry}")
    handle_revision(entry)