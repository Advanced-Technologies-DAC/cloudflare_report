TEST_REQ = {
    "title": "Requests",
    "content": {
        "2025-02-18": 2149,
        "2025-02-19": 3170,
        "2025-02-21": 1409,
        "2025-02-20": 3497,
        "2025-02-17": 2038,
        "2025-02-23": 2606,
        "2025-02-22": 2750,
    },
    "type": "numeric",
}

TEST_CACHED_REQ = {
    "title": "Cached Requests",
    "content": {
        "2025-02-18": 78,
        "2025-02-19": 91,
        "2025-02-21": 48,
        "2025-02-20": 82,
        "2025-02-17": 96,
        "2025-02-23": 21,
        "2025-02-22": 29,
    },
    "type": "numeric",
}

TEST_BANDWIDTH = {
    "title": "Bandwidth",
    "content": {
        "2025-02-18": 10500001,
        "2025-02-19": 11846936,
        "2025-02-21": 9085397,
        "2025-02-20": 12351202,
        "2025-02-17": 10330733,
        "2025-02-23": 10485650,
        "2025-02-22": 10649039,
    },
    "type": "byte",
}

TEST_CACHED_BANDWIDTH = {
    "title": "Cached Bandwidth",
    "content": {
        "2025-02-18": 70076,
        "2025-02-19": 86224,
        "2025-02-21": 33857,
        "2025-02-20": 76398,
        "2025-02-17": 104240,
        "2025-02-23": 8367,
        "2025-02-22": 16645,
    },
    "type": "byte",
}

TEST_VISITS = {
    "title": "Visits",
    "content": {
        "2025-02-18": 170,
        "2025-02-19": 173,
        "2025-02-21": 179,
        "2025-02-20": 208,
        "2025-02-17": 164,
        "2025-02-23": 130,
        "2025-02-22": 115,
    },
    "type": "numeric",
}

TEST_HTTP_VERSIONS = {
    "title": "HTTP Versions",
    "content": {
        "HTTP/1.0": 36,
        "HTTP/1.1": 14206,
        "HTTP/2": 2998,
        "HTTP/3": 378,
        "UNK": 1,
    },
    "type": "numeric",
}

TEST_CONTENT_TYPE = {
    "title": "Content Type",
    "content": {
        "empty": 248,
        "js": 203,
        "json": 2624,
        "bin": 57,
        "rss": 3,
        "html": 14431,
        "txt": 53,
    },
    "type": "numeric",
}

TEST_SSL_VERSIONS = {
    "title": "SSL Versions",
    "content": {"unknown": 1, "none": 6601, "TLSv1.2": 6213, "TLSv1.3": 4804},
    "type": "numeric",
}

TEST_REQUESTS_PER_COUNTRY = {
    "title": "Requests per country",
    "content": {"US": 7845, "IE": 7076, "CH": 646, "NL": 338, "SG": 334},
    "type": "numeric",
}


# dashboard_stat_test(TEST_VISITS, "Visits")
# dashboard_table_map(TEST_REQUESTS_PER_COUNTRY)
# dashboard_stat_graph(TEST_REQ, TEST_CACHED_REQ, "Uncached requests", "Requests")
# dashboard_stat_graph(TEST_BANDWIDTH, TEST_CACHED_BANDWIDTH, "Uncached bandwidth", "MB")
# dashboard_pie_bar(TEST_HTTP_VERSIONS, TEST_SSL_VERSIONS, TEST_CONTENT_TYPE)

# print(get_requests(ATDAC_ID, "2025-02-23", 7))
# print(get_bandwidth(ATDAC_ID, "2025-02-23", 7))
# print(get_visits(ATDAC_ID, "2025-02-23", 7))
# print(get_views(ATDAC_ID, "2025-02-23", 7))
# print(get_http_versions(ATDAC_ID, "2025-02-23", 7))
# print(get_ssl_traffic(ATDAC_ID, "2025-02-23", 7))
# print(get_content_type(ATDAC_ID, "2025-02-23", 7))
# print(get_cached_requests(ATDAC_ID, "2025-02-23", 7))
# print(get_cached_bandwidth(ATDAC_ID, "2025-02-23", 7))
# print(get_encrypted_bandwidth(ATDAC_ID, "2025-02-23", 7))
# print(get_encrypted_requests(ATDAC_ID, "2025-02-23", 7))
# print(get_fourxx_errors(ATDAC_ID, "2025-02-23", 7))
# print(get_fivexx_errors(ATDAC_ID, "2025-02-23", 7))
# print(get_zones(TOKEN, ID))
# print(get_accounts(TOKEN, ID))
# print(get_account_settings(TOKEN, ID))
# print(get_requests_per_location(ATDAC_ID, "2025-02-23", 7))
# print(get_requests_per_location(ATDAC_ID, "2025-02-23", 7))
# print(get_bandwidth_per_location(ATDAC_ID, "2025-02-23", 7))
