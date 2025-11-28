DATE_TIME_STANDARD_FMT = "%Y-%m-%d %H.%M"
DATE_STANDARD_FMT = "%Y-%m-%d"
DATE_STANDARD_MONTH = "%Y-%m"

TEST_DATE = "2025-01-01"
TEST_DATE_2= "2025-01-02"

TEST_REQ_SUCC = "SUCCESS"
TEST_REQ_INVALID = "INVALID"
TEST_REQ_ERR = "ERROR"

TEST_USR_EXIST = "EXISTENT"

USG_DB_TIERS = "subscription_tiers"
USG_DB_USERS = "user_subscriptions"
USG_DB_USAGE = "daily_usage"

USG_DB_COLLECTIONS = [USG_DB_TIERS, USG_DB_USERS, USG_DB_USAGE]

USG_DB_TIERS_INFO = [
    {
        "tier_name": "free",
        "monthly_limit": 50,
        "price_usd": 0.00
    },
    {
        "tier_name": "basic",
        "monthly_limit": 200,
        "price_usd": 9.99
    },
    {
        "tier_name": "pro",
        "monthly_limit": 1000,
        "price_usd": 29.99
    },
    {
        "tier_name": "unlimited",
        "monthly_limit": -1,
        "price_usd": 99.99
    }]

HTML_TAGS_TO_REMOVE = {
    # Scripting and styling
    'script',  # JavaScript code
    'style',  # CSS styling rules
    'noscript',  # Fallback content for disabled JavaScript
    'code',  # Code blocks
    'pre',  # Preformatted text

    # Metadata and resources
    'meta',  # Page metadata (charset, description, etc.)
    'link',  # External resource links (CSS, favicons, etc.)

    # Navigation and UI elements
    'nav',  # Navigation menus
    'header',  # Page header sections
    'footer',  # Page footer sections
    'aside',  # Sidebar content
    'menu',  # Menu elements
    'button',  # Buttons (unlikely to contain event info)

    # Forms and interactive elements
    'form',  # Forms
    'input',  # Input fields
    'select',  # Dropdowns
    'textarea',  # Text areas

    # Media elements
    'img',  # Images
    'svg',  # Scalable vector graphics
    'video',  # Video players
    'audio',  # Audio players
    'canvas',  # Canvas elements
    'picture',  # Picture elements
    'source',  # Media sources

    # Embedded content
    'iframe',  # Inline frames (embedded pages, widgets)
    'embed',  # Embedded content

    # Advertising and tracking
    'ads',  # Ad containers (custom tag)
    'advertisement',  # Advertisement sections
}

HTML_TAGS_TO_KEEP = {
    # Text content
    'html', 'head', 'body', 'p', 'span', 'div', 'section', 'article', 'main',

    # Headings
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',

    # Lists
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',

    # Text formatting (semantic content)
    'strong', 'b', 'em', 'i', 'mark', 'small', 'del', 'ins', 'sub', 'sup',

    # Tables (if events in tables)
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th', 'caption',

    # Semantic content
    'time', 'address', 'blockquote', 'q', 'cite',

    # Links (event links are important!)
    'a',

    # Other potentially useful
    'label', 'legend', 'figcaption', 'details', 'summary',
}