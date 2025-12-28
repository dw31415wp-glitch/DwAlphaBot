# Processing a list of pages

The basic function of this bot is:

1. Read multiple lists of RfC's
1. Read each page containing an RfC
1. Find the Talk section containing the RfC
1. Get the list of replies to an RfC
1. Collect statistics about each comment of each RfC

## Map Reduce architecture

A map reducer pattern works well for this problem. Considering that a starting list will create more lists and each will need to be processed.

A good way to do this in Python is:
