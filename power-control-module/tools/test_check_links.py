"""Link checks for the design documents (standard library only)."""

from check_links import anchors, broken_links, slug


def test_documents_have_no_broken_links():
    assert broken_links() == []


def test_slugs_match_github():
    assert slug("Rear floods (Hobbs halogen)") == "rear-floods-hobbs-halogen"
    assert slug("J7 — AUX and keep-alive outputs") == "j7--aux-and-keep-alive-outputs"


def test_headings_inside_code_blocks_do_not_count():
    assert anchors("# Title\n\n```bash\n# not a heading\n```\n") == {"title"}
