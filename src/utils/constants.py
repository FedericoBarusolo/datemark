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