import pytest
from bs4 import BeautifulSoup

from utils import html_parse as html
from utils import constants as cst


@pytest.mark.unit
@pytest.mark.parametrize("soup,output",
                         [
                             (BeautifulSoup("", "html.parser"),
                              BeautifulSoup("", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             # Badly formatted html are handled by soup
                             (BeautifulSoup("<a>Hello!</b><c>", "html.parser"),
                              BeautifulSoup("<a>Hello!<c></c></a>", "html.parser")),

                             (BeautifulSoup("<!-- This is a comment --><a>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<!-- This is a comment --><a>Hello!</a><!-- <a>Goodbye!</a> -->",
                                            "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<!-- This is a comment <a>Hello!</a><a>Goodbye!</a> -->",
                                            "html.parser"),
                              BeautifulSoup("", "html.parser"))
                         ])
def test_remove_comments(soup, output):
    html.remove_comments(soup)

    assert soup == output


@pytest.mark.unit
@pytest.mark.parametrize("soup,output",
                         [
                             (BeautifulSoup("", "html.parser"),
                              BeautifulSoup("", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<a name='greeting'>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),
                         ])
def test_clear_tags_attributes(soup, output):
    html.clear_tags_attributes(soup)

    assert soup == output


@pytest.mark.unit
@pytest.mark.parametrize("soup,output",
                         [
                             (BeautifulSoup("", "html.parser"),
                              BeautifulSoup("", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup(f"<a>Hello!</a>"
                                            f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed</{t}>",
                                            "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup(f"<a>Hello!</a>"
                                            f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed"
                                                f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[1])}>this will be removed too"
                                                f"</{t1}>"
                                            f"</{t}>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup(f"<a>Hello!"
                                                f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed</{t}>"
                                                f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_KEEP))[1])}>this will be kept</{t1}>"
                                            "</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!"
                                                f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_KEEP))[1])}>this will be kept</{t1}>"
                                            "</a>", "html.parser")),

                             # For unknown tags (not in whitelist), keep the content only
                             (BeautifulSoup(f"<a>Hello!"
                                                f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed</{t}>"
                                                f"<randomTagType>this will be kept, but without tags</randomTagType>"
                                            "</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!this will be kept, but without tags</a>", "html.parser")),

                             # Remove all nested tags inside blacklisted ones, no matter what type (even TAGS_TO_KEEP)
                             (BeautifulSoup(f"<a>Hello!</a>"
                                            f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed"
                                                f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_KEEP))[1])}>this will be removed too"
                                                f"</{t1}>"
                                            f"</{t}>"
                                            f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_KEEP))[1])}>this will be kept"f"</{t1}>",
                                            "html.parser"
                                            ),
                              BeautifulSoup("<a>Hello!</a>"f"<{(t1:=sorted(list(cst.HTML_TAGS_TO_KEEP))[1])}>this will be kept"
                                            f"</{t1}>",
                                            "html.parser")),
                         ])
def test_filter_html_tags(soup, output):
    html.filter_html_tags(soup)

    # comparing string content due to some strange soup object inequality after .unwrap (unknown tags)
    assert str(soup) == str(output)


@pytest.mark.unit
@pytest.mark.parametrize("soup,output",
                         [
                             (BeautifulSoup("", "html.parser"),
                              BeautifulSoup("", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a><a></a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a><a><b></b></a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a><a><b>Hello!</b></a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a></a><a><b>Hello!</b></a>", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a><a><b>Hello!</b><c></c></a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a></a><a><b>Hello!</b></a>", "html.parser")),

                             (BeautifulSoup("<a>Hello!</a><a><b>Hello!</b><c><d></d></c></a>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a></a><a><b>Hello!</b></a>", "html.parser")),

                             # Badly formatted html are handled by soup
                             (BeautifulSoup("<a>Hello!</a><a></b>", "html.parser"),
                              BeautifulSoup("<a>Hello!</a>", "html.parser")),
                         ])
def test_remove_empty_recursive(soup, output):
    html.remove_empty_recursive(soup)

    assert soup == output

@pytest.mark.unit
@pytest.mark.parametrize("html_file,output",
                         [
                             ("<!-- I want my title to be super-mega bold!!! -->"
                              "<h1 style='megabold'>Title</h1>"
                              f"<{(t:=sorted(list(cst.HTML_TAGS_TO_REMOVE))[0])}>this will be removed"f"</{t}>"
                              "<a><a><a></a></a>Hello!</a>"
                              "See you in London<br>UK",

                              "<h1>Title</h1>"
                              "<a>Hello!</a>"
                              "See you in London\nUK")
                         ])
def test_clean_html_string(html_file, output):
    assert html.clean_html_string(html_file) == output