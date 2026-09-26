from obsidian_exporter.text import html_to_text


def test_html_to_text_removes_media_and_keeps_text():
    html = '<div>Hello <b>world</b><br><img src="x.png"> [sound:voice.mp3]</div>'

    assert html_to_text(html) == "Hello **world**"


def test_html_to_text_keeps_external_links_functional():
    html = '<a href="https://example.com">Example</a><audio src="a.mp3"></audio>'

    assert html_to_text(html) == "[Example](https://example.com)"


def test_html_to_text_keeps_bare_urls_and_formatting():
    html = '<p>See <b>important</b> https://example.com/path?q=1 now</p>'

    assert html_to_text(html) == "See **important** https://example.com/path?q=1 now"


def test_html_to_text_removes_bracket_artifacts_without_breaking_links():
    html = '<p>Word[text1]:;[text2] <a href="https://example.com">Example</a></p>'

    assert html_to_text(html) == "Word [Example](https://example.com)"


def test_html_to_text_decodes_entities_and_normalizes_whitespace():
    html = "<p>one&nbsp;&amp;&nbsp;two</p><p>three</p>"

    assert html_to_text(html) == "one & two\n\nthree"
