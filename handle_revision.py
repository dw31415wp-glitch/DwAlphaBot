
from datetime import datetime
from pydoc import text
import mwparserfromhell
from pywikibot.time  import Timestamp
from pywikibot import textlib
from config import site

from pywikibot.diff import html_comparator

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

def print_removed_entries(entry, print_keys, diff_table=None):
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

    print(f'== Removed RFC Entries ==')
    for rfc_text in rfc_texts:
        user, rfc_datetime = extract_user_and_date(rfc_text)
        print(f"RFC Text:\n{rfc_text}\nUser: {user}, Date: {rfc_datetime}\n")




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




def handle_revision(entry: dict):
    print_keys = ['revid', 'parentid', 'timestamp', 'user', 'comment']
    if 'removed' in entry.get('comment', '').lower():
        print_removed_entries(entry, print_keys, entry.get('diff_table'))

if __name__ == "__main__":
    #entry = {'revid': 1063078964, 'parentid': 1062709000, 'timestamp': Timestamp(2022, 1, 1, 3, 1, 22), 'user': 'Legobot', 'comment': 'Removed: [[Wikipedia talk:Notability (organizations and companies)]].', 'diff_table': '<tr>\n  <td colspan="2" class="diff-lineno">Line 55:</td>\n  <td colspan="2" class="diff-lineno">Line 55:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>(Editors {{u|Binksternet}}, {{u|Black Kite}}, {{u|FormalDude}} expressed opinions above). &lt;s&gt;Also, @ {{u|CAMERAwMUSTACHE}}, {{u|ChicagoWikiEditor}}, {{u|FMSky}} if they have time for suggestions, would be welcome&lt;/s&gt;.</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>(Editors {{u|Binksternet}}, {{u|Black Kite}}, {{u|FormalDude}} expressed opinions above). &lt;s&gt;Also, @ {{u|CAMERAwMUSTACHE}}, {{u|ChicagoWikiEditor}}, {{u|FMSky}} if they have time for suggestions, would be welcome&lt;/s&gt;.</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>[[User:Cornerstonepicker|Cornerstonepicker]] ([[User talk:Cornerstonepicker|talk]]) 02:13, 3 December 2021 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>[[User:Cornerstonepicker|Cornerstonepicker]] ([[User talk:Cornerstonepicker|talk]]) 02:13, 3 December 2021 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Wikipedia talk:Notability (organizations and companies)#rfc_4ED494F|Wikipedia talk:Notability (organizations and companies)]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the line {{tq|The scope of this guideline covers all groups of people organized together for a purpose with the exception of non-profit educational institutions, religions or sects, and sports teams.}} be altered to state:</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'A\'\'\': That esports are within the scope of this notability guideline</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'B\'\'\': That esports are not within the scope of this notability guideline</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>*\'\'\'C\'\'\': No change</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><br /></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>This RfC is proposed in the context of the no consensus [[Wikipedia:Articles for deletion/Stalwart Esports (2nd nomination)|Stalwart Esports AfD]] where the closer opined that there was a "real need" for guidance on which guideline or policy was controlling.</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>02:32, 2 December 2021 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{RFC list footer|bio|hide_instructions={{{hide_instructions}}} }}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{RFC list footer|bio|hide_instructions={{{hide_instructions}}} }}</div></td>\n</tr>\n', 'page_title': 'Wikipedia:Requests_for_comment/Biographies', 'year': 2022}
    entry = {'revid': 1000204955, 'parentid': 1000195870, 'timestamp': Timestamp(2021, 1, 14, 3, 1, 30), 'user': 'Legobot', 'comment': 'Removed: [[Talk:Arthur Laffer]] [[Talk:Ted Cruz]] [[Talk:Emily VanDerWerff]].', 'diff_table': '<tr>\n  <td colspan="2" class="diff-lineno">Line 21:</td>\n  <td colspan="2" class="diff-lineno">Line 21:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>Here we go again. [[User:Artixxxl|Artixxxl]] is adding to the list people who are not Ukrainian citizens, who were not born in Ukraine (or area which is now Ukraine) and never lived there, on the nasis that they have Ukrainian ancestry (one example of [[Alexei Navalny]] spending summers with his grandparents - which I personally find completely ridiculous; in this way everybody who was on holidays in Crimea between 1954 and 2014 - or even possibly after 2014 - can be added to the list) and this would make the list potentially of infinite size - even I would qualify for inclison. Therefore we need to define the scope very clearly. Below I list categories of notable individuals, please argue whether these need to be included.--[[User:Ymblanter|Ymblanter]] ([[User talk:Ymblanter|talk]]) 10:06, 1 January 2021 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>Here we go again. [[User:Artixxxl|Artixxxl]] is adding to the list people who are not Ukrainian citizens, who were not born in Ukraine (or area which is now Ukraine) and never lived there, on the nasis that they have Ukrainian ancestry (one example of [[Alexei Navalny]] spending summers with his grandparents - which I personally find completely ridiculous; in this way everybody who was on holidays in Crimea between 1954 and 2014 - or even possibly after 2014 - can be added to the list) and this would make the list potentially of infinite size - even I would qualify for inclison. Therefore we need to define the scope very clearly. Below I list categories of notable individuals, please argue whether these need to be included.--[[User:Ymblanter|Ymblanter]] ([[User talk:Ymblanter|talk]]) 10:06, 1 January 2021 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Ted Cruz#rfc_76C58B0|Talk:Ted Cruz]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the lead section conclude with one sentence about his family (being that two of his family members meet the Wikipedia criteria of notability itself by having articles), just like most large biographies of living persons typically do, in a neutral manner and without giving an inference of perceived "inherited notability" and / or granting notability to the subject? Or is it really against a policy and does the one sentence make the article about them? I’m here to get consensus as I allegedly didn’t do that by including something I assumed to be a non-issue in its ubiquity. And that I’ve seen nothing in the Manual of Style explicitly against it. [[User:Trillfendi|Trillfendi]] ([[User talk:Trillfendi|talk]]) 22:23, 29 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Emily VanDerWerff#rfc_C9A3824|Talk:Emily VanDerWerff]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should the article include the subject\'s previous name in the opening paragraph? This has been omitted citing [[WP:DEADNAME]] because a previous version of this article was deleted. Does the fact that a previous version was deleted prove that the subject was not notable at the time? If so, does this proof satisfy [[WP:DEADNAME]], specifically that {{tq|the birth name should be included in the lead sentence only if the person was notable under that name}}?</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><br /></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Previous discussion of this question starts [https://en.wikipedia.org/wiki/Talk:Emily_VanDerWerff#Birth_name above]. [https://en.wikipedia.org/w/index.php?title=Emily_VanDerWerff&amp;oldid=996643305 Here] is a revision showing how it might appear. \'\'\'[[User:Careless hx|carelesshx]]\'\'\' &lt;sub&gt;[[User talk:Careless hx|talk]]&lt;/sub&gt; 16:04, 28 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>\'\'\'[[Talk:Donald Gary Young#rfc_F9665B6|Talk:Donald Gary Young]]\'\'\'</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>\'\'\'[[Talk:Donald Gary Young#rfc_F9665B6|Talk:Donald Gary Young]]\'\'\'</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td colspan="2" class="diff-lineno">Line 44:</td>\n  <td colspan="2" class="diff-lineno">Line 36:</td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>Should the lead note that Black wrote a "flattering biography of Donald Trump" and that he was pardoned \'\'by President Trump\'\'? Currently, the lead says Black was pardoned but it doesn\'t say by whom, and it doesn\'t include the context that Black had just prior to the pardon released a hagiography of Trump. (Original timestamp: 12:55, 13 May 2020) [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:35, 24 December 2020 (UTC)}}</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>Should the lead note that Black wrote a "flattering biography of Donald Trump" and that he was pardoned \'\'by President Trump\'\'? Currently, the lead says Black was pardoned but it doesn\'t say by whom, and it doesn\'t include the context that Black had just prior to the pardon released a hagiography of Trump. (Original timestamp: 12:55, 13 May 2020) [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:35, 24 December 2020 (UTC)}}</div></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>\'\'\'[[Talk:Arthur Laffer#rfc_1AAC44C|Talk:Arthur Laffer]]\'\'\'</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker" data-marker="−"></td>\n  <td class="diff-deletedline diff-side-deleted"><div>Should we add a paragraph to the article that mentions: (i) that Laffer is advising the trump administration on dealing with the coronavirus, and (ii) the policies that Laffer has advocated for in dealing with the coronavirus pandemic? [[User:Snooganssnoogans|Snooganssnoogans]] ([[User talk:Snooganssnoogans|talk]]) 05:33, 24 December 2020 (UTC)}}</div></td>\n  <td colspan="2" class="diff-empty diff-side-added"></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>\'\'\'[[Talk:Arthur Laffer#rfc_6BDAC22|Talk:Arthur Laffer]]\'\'\'</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>\'\'\'[[Talk:Arthur Laffer#rfc_6BDAC22|Talk:Arthur Laffer]]\'\'\'</div></td>\n</tr>\n<tr>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-deleted"><div>{{rfcquote|text=</div></td>\n  <td class="diff-marker"></td>\n  <td class="diff-context diff-side-added"><div>{{rfcquote|text=</div></td>\n</tr>\n', 'page_title': 'Wikipedia:Requests_for_comment/Biographies', 'year': 2021}
    print(f"Handling revision: {entry}")
    handle_revision(entry)