import section_utils


def test_get_comments_from_section_text_with_headings():
    """Test extracting sections with multiple headings."""
    text = """== First Comment ==
This is the first comment.

== Second Comment ==
This is the second comment.

== Third Comment ==
This is the third comment.
"""
    sections = section_utils.get_comments_from_section_text(text)
    
    assert len(sections) >= 3
    assert sections[0]["heading"] == "First Comment"
    assert "first comment" in sections[0]["text"].lower()
    assert sections[1]["heading"] == "Second Comment"
    assert "second comment" in sections[1]["text"].lower()
    assert sections[2]["heading"] == "Third Comment"
    assert "third comment" in sections[2]["text"].lower()


def test_get_comments_from_section_text_no_headings():
    """Test with plain text (no headings)."""
    text = "This is just plain text without any headings."
    sections = section_utils.get_comments_from_section_text(text)
    
    assert len(sections) == 1
    assert sections[0]["heading"] == ""
    assert sections[0]["text"] == text


def test_get_comments_from_section_text_with_leading_content():
    """Test with content before first heading."""
    text = """Initial content here.

== First Comment ==
Comment content.
"""
    sections = section_utils.get_comments_from_section_text(text)
    
    assert len(sections) == 2
    assert sections[0]["heading"] == ""
    assert "Initial content" in sections[0]["text"]
    assert sections[1]["heading"] == "First Comment"
    assert "Comment content" in sections[1]["text"]


def test_get_comments_from_section_text_varied_heading_levels():
    """Test with different heading levels (==, ===, ====)."""
    text = """== Level 2 ==
Content at level 2.

=== Level 3 ===
Content at level 3.

==== Level 4 ====
Content at level 4.
"""
    sections = section_utils.get_comments_from_section_text(text)
    
    assert len(sections) == 3
    assert sections[0]["heading"] == "Level 2"
    assert sections[1]["heading"] == "Level 3"
    assert sections[2]["heading"] == "Level 4"


def test_get_comments_with_rfc_section():
    """Test with a real RFC section (North Korea Infobox RfC example)."""
    text = """== RfC on Infobox Ideology ==

Should the Infobox ideology be changed?

:'''Oppose''': The form of government never changed.

:Support changing to '''socialist''': Though I'd prefer more sources.

:'''Bad Rfc''' we already had consensus...
"""
    sections = section_utils.get_comments_from_section_text(text)
    
    assert len(sections) >= 1
    assert sections[0]["heading"] == "RfC on Infobox Ideology"
    assert "Should the Infobox" in sections[0]["text"]
    assert "Oppose" in sections[0]["text"]
