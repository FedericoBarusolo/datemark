from bs4 import BeautifulSoup, Comment, Tag

from utils import constants as cst


def remove_comments(soup: BeautifulSoup) -> None:
    """
    Remove all HTML comments from the BeautifulSoup object.

    Finds and extracts all comment nodes from the parsed HTML document,
    modifying the soup object in place.

    Args:
        soup: The BeautifulSoup object to process.

    Returns:
        None. The soup object is modified in place.
    """
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    return


def clear_tags_attributes(soup: BeautifulSoup) -> None:
    """
    Remove all attributes from all HTML tags.

    Strips all attributes (like class, id, style, etc.) from every tag
    in the document, leaving only the tag names and their content.

    Args:
        soup: The BeautifulSoup object to process.

    Returns:
        None. The soup object is modified in place.
    """
    for tag in soup.find_all(True):
        tag.attrs = {}

    return


def filter_html_tags(soup: BeautifulSoup) -> None:
    """
    Filter HTML tags based on whitelist and removal configurations.

    Removes tags specified in HTML_TAGS_TO_REMOVE completely (including
    their content), and unwraps tags not in HTML_TAGS_TO_KEEP (preserving
    their content but removing the tag itself).

    Blacklisting is done before whitelisting, therefore whitelisted tags
    will be removed if nested inside blacklisted ones.

    Args:
        soup: The BeautifulSoup object to process.

    Returns:
        None. The soup object is modified in place.
    """
    # Completely remove unwanted tags
    for tag_name in cst.HTML_TAGS_TO_REMOVE:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Unwrap everything else not in whitelist
    for tag in soup.find_all(True):
        if tag.name not in cst.HTML_TAGS_TO_KEEP:
            tag.unwrap()

    return


def remove_empty_recursive(soup: Tag | BeautifulSoup) -> None:
    """
    Recursively remove empty tags from the HTML structure.

    Traverses the HTML tree in post-order, removing tags that contain no
    meaningful text content and no child tags. This cleanup helps eliminate
    structural artifacts left by previous filtering operations.

    Args:
        soup: The BeautifulSoup object or Tag to process recursively.

    Returns:
        None. The soup object is modified in place.
    """
    if str(soup) == "":
        return

    # Process children first (post-order traversal)
    for child in list(soup.contents):
        if hasattr(child, "contents"):  # it's a tag, not a string
            remove_empty_recursive(child)

    # After children are processed, check if this tag is empty
    # Condition: no meaningful text + no non-text children
    text = soup.get_text(strip=True)

    has_child_tag = any(hasattr(c, "name") for c in soup.contents)

    if not text and not has_child_tag:
        soup.decompose()

    return


def clean_html_string(html: str) -> str:
    """
    Clean and simplify an HTML string by applying multiple filters.

    Processes raw HTML through a series of cleaning operations: removes
    comments, filters tags based on whitelist/blacklist, strips all
    attributes, and removes empty tags. The result is a simplified HTML
    structure containing only essential content.

    Args:
        html: The raw HTML string to clean.

    Returns:
        The cleaned HTML as a string with simplified structure and content.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Before removing tags, handle self-closing tags
    for br in soup.find_all(['br', 'hr']):
        br.replace_with('\n')

    remove_comments(soup)
    filter_html_tags(soup)
    clear_tags_attributes(soup)
    remove_empty_recursive(soup)

    return str(soup)