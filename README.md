## DwAlphaBot

Collects statistics about RfC's. Based on SodiumBot. Requires two config files like any pywikibot:

- user-config.py
- user-password.cfg
- config.py can be used for source controlled parameters, like years to run

TODO: Move years to run into a command line parameter

### Run

```bash
python main.py
```

### Dev Setup

```bash
source venv ./.venv/bin/activate
pip install -r requirements.txt
```

## RfC History

1. First collect the statistics to a local DB (not in source control)
1. Second publish

```bash
python main.py -j collect_rfc_history
python main.py -j publish_history
```
