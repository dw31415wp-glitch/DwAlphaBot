import find_rfc


class DummyPage:
    def __init__(self, *args):
        if len(args) == 2:
            self._title = args[1]
        else:
            self._title = args[0]

    def title(self):
        return self._title

    def exists(self):
        return True

    @property
    def text(self):
        if self._title == "RFCList":
            return "This is the RFC list page content"
        return f"page {self._title}"

    def linkedPages(self):
        if self._title == "RFCList":
            return [DummyPage("User:Bob"), DummyPage("Some RFC"), DummyPage("Wikipedia:Requests for comment")]
        return []


def test_is_not_other_list_page():
    assert not find_rfc.is_not_other_list_page(DummyPage("Wikipedia:Requests for comment"))
    assert find_rfc.is_not_other_list_page(DummyPage("Some RFC"))


def test_is_not_user_page():
    assert not find_rfc.is_not_user_page(DummyPage("User:Alice"))
    assert find_rfc.is_not_user_page(DummyPage("Talk:Someone"))


def test_get_rfc_list_filters_and_prints(monkeypatch, capsys):
    monkeypatch.setattr(find_rfc, "Page", DummyPage)
    monkeypatch.setattr(find_rfc, "LIST_OF_RFC_PAGES", ["RFCList"])
    monkeypatch.setattr(find_rfc, "site", "dummy_site")

    find_rfc.get_rfc_list()

    captured = capsys.readouterr()
    out = captured.out
    assert "RFC Pages to monitor:" in out
    assert "- RFCList" in out
    assert "Some RFC" in out
    assert "User:Bob" not in out
    assert "Requests for comment" not in out
