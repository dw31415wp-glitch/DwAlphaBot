

common_words = {
    'rfcquote': 1000,
    'text': 1000,
    'user': 1000,
    'talk': 1000,
    'rfc': 1000,
    'the': 1000,
    'and': 1000,
    'a': 1000,
    'of': 1000,
    'to': 1000,
    'in': 1000,
    'is': 1000,
    'that': 1000,
    'it': 1000,
    'as': 1000,
    'for': 1000,
    'on': 1000,
    'with': 1000,
    'this': 1000,
    'by': 1000,
    'an': 1000,
    'be': 1000,
}

def remove_common_words(word_list) -> list[str]:
    """
    Removes common words from the provided list of words.

    Parameters:
    word_list (list of str): The list of words to filter.

    Returns:
    list of str: A list of words with common words removed.
    """

    # Load common words if not already loaded
    # add words to count dictionary
    global common_words

    for word in word_list:
        word_lower = word.lower()
        if word_lower in common_words:
            common_words[word_lower] += 1
        else:
            common_words[word_lower] = 1
    # Filter out common words
    filtered_words = [word for word in word_list if common_words.get(word.lower(), 0) < 10]

    # trim list of filtered words to max 1000
    if len(filtered_words) > 1000:
        # get the least common words first
        filtered_words.sort(key=lambda w: common_words.get(w.lower(), 0))
        # keep only the first 1000
        filtered_words = filtered_words[:1000]
        # remove keys from common_words that are not in filtered_words
        filtered_set = set(word.lower() for word in filtered_words)
        common_words = {word: count for word, count in common_words.items() if word in filtered_set}

    # return unique words only
    filtered_words = list(dict.fromkeys(filtered_words))

    return filtered_words

def extract_words(text) -> str:
    """
    Extracts words from the given text. A word is defined as a sequence of
    alphabetic characters (a-z, A-Z). Non-alphabetic characters are treated
    as delimiters.

    Parameters:
    text (str): The input text from which to extract words.

    Returns:
    str: A string of extracted words separated by spaces.
    """
    import re

    # Use regular expression to find all sequences of alphabetic characters
    words = re.findall(r'[a-zA-Z]+', text)
    # Remove common words
    words = remove_common_words(words)

    # take the first 20 words
    words = words[:20]

    return " ".join(words)

if __name__ == "__main__":
    sample_text = """
{{rfcquote|text=
Prominent, reliable sources give both 1969 and 1970 as birth years for Mariah Carey. How should this be addressed?


* '''Comment'''  The only source for Mariah's Carey birth year that cites actual, physical documentation is [[Time Inc.]]'s ''[[People (magazine)|People]]'' magazine, a highly [[WP:RS|reliable source]], which says [http://www.nndb.com/people/115/000023046/#FN1 here]:
{{quote|"[W]e have a copy of Ms. Carey's driver's license, which lists her birthday as March 27, 1969. Furthermore, we spoke with the administrators at the high school she attended who confirmed that Ms. Carey's birthday is March 27, 1969, as did her management when we made our initial interview."}}
Carey herself, in her U.S. Copyright registration, also gives 1969 [http://cocatalog.loc.gov/cgi-bin/Pwebrecon.cgi?v1=1&ti=1,1&Search_Arg=Mariah%20Carey&Search_Code=TALL&CNT=25&PID=AkB0SNBj680EIAiGvc53x9JVOTXmi&SEQ=20130809091350&SID=2 here]. 

Given that ''People'' obtained confirmation from  the driver's license, from the her date in her high school records, as well as from her management, and that '''Carey herself''' at the beginning of her career said 1969, how can this documentation be considered insufficient? --[[User:Tenebrae|Tenebrae]] ([[User talk:Tenebrae|talk]]) 13:21, 9 August 2013 (UTC)}}
"""

    extracted_words = extract_words(sample_text)
    print(extracted_words)