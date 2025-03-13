"""
V5 functions neccesary to run the Cloudflare API
"""

__version__ = "5.0.0"


from datetime import datetime, timedelta

import requests


def range_generator(leq_date: str, periods: int) -> dict:
    """
    Generates the end date for the query by sbstracting a specified number of periods from the start date.
    Args:
        start_date (str): Start of the date range (ISO 8601 format).
        periods (int): Num. of periods after the start_date (days to substract)
    Returns:
        dict: A dictionary with:
            - "leq_date": The end date of the range in ISO 8601 format with time appended as "23:59:59Z".
            - "geq_date": The start date of the range in ISO 8601 format with time appended as "00:00:00Z".
    Raises:
        ValueError: If the start_date format is invalid or periods in negative
    """
    if periods < 0:
        raise ValueError("Periods must be a non-negative integer.")
    days_to_subtract = periods - 1
    try:
        end = datetime.strptime(leq_date, "%Y-%m-%d")
        start = end - timedelta(days=days_to_subtract)
        return {
            "leq_date": end.strftime("%Y-%m-%dT23:59:59Z"),
            "geq_date": start.strftime("%Y-%m-%dT00:00:00Z"),
        }
    except ValueError as e:
        raise ValueError(
            f"Invalid date format: '{leq_date}'. Use ISO 8601 format 'YYYY-MM-DD'."
        ) from e


def execute_query(query: str, variables: dict) -> None:
    """
    Execute GraphQL query.
    Args:
        query (str): GraphQL query string.
        variables (dict): Variables for the query.
    """
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"query": query, "variables": variables}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")


def get_accounts(token: str) -> dict:
    """
    Retrieve basic information for all Cloudflare accounts accessible with the provided token.
    Args:
        token (str): API token for authorization.
    Returns:
        dict: A dictionary containing account names as keys and their respective IDs as values.
    Raises:
        Exception: If the HTTP request fails or the API returns errors.
    """
    url = "https://api.cloudflare.com/client/v4/accounts"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    results = {account["name"]: account["id"] for account in data["result"]}
    return results


def get_zones(token: str) -> dict:
    """
    Retrieve zone names and their corresponding IDs from Cloudflare.
    Args:
        token (str): API token for authorization.
    Returns:
        dict: A dictionary with zone names as keys and their respective IDs as values.
    Raises:
        Exception: If the HTTP request fails or the Cloudflare API returns errors.
    """
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text}")
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API Error: {data.get('errors')}")
    results = {zone["name"]: zone["id"] for zone in data.get("result", [])}
    return results


# Stats Module
def get_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of requests per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format (YYYY-MM-DD).
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective request counts as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetZoneRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            requests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No request data available in the response.")
        request_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["requests"]
            for item in request_totals
        }
        return {"title": "Requests", "content": results, "type": "numeric"}
    except (KeyError, IndexError) as e:
        raise Exception(f"Error processing response: {e}")


def get_requests_per_location(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetRequestsLocations($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            countryMap {
                                clientCountryName
                                requests
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No location data available in the response.")
        location_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in location_totals:
            for country in daily["sum"]["countryMap"]:
                country_name = country["clientCountryName"]
                requests = country["requests"]
                results[country_name] = results.get(country_name, 0) + requests
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True)[:5]
        )
        return {
            "title": "Requests per country",
            "content": sorted_results,
            "type": "numeric",
        }
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total bandwidth per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetZoneBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            bytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No bandwidth data available in the response.")
        bandwidth_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["bytes"]
            for item in bandwidth_totals
        }
        return {"title": "Bandwidth", "content": results, "type": "byte"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_bandwidth_per_location(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total bandwidth per country for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing countries as keys and their respective bandwidth (in bytes) as values.
    """
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetBandwidthLocations($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            countryMap {
                                clientCountryName
                                bytes
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No bandwidth data available in the response.")
        location_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in location_totals:
            for country in daily["sum"]["countryMap"]:
                country_name = country["clientCountryName"]
                bandwidth = country["bytes"]
                results[country_name] = results.get(country_name, 0) + bandwidth
        sorted_results = dict(
            sorted(results.items(), key=lambda item: item[1], reverse=True)[:10]
        )
        return {
            "title": "Bandwidth per country",
            "content": sorted_results,
            "type": "byte",
        }
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_visits(zone_tag: str, leq_date: str, periods: int) -> dict:
    """
    Retrieve the total number of visits per day for a specific zone within a given time range.
    Args:
        zone_tag (str): Unique identifier for the Cloudflare zone.
        leq_date (str): End date of the range (inclusive) in ISO 8601 format ("YYYY-MM-DD").
        periods (int): Number of days before the end date to include in the range.
    Returns:
        dict: A dictionary containing dates as keys and their respective visit counts as values.
    """
    range_generated = range_generator(leq_date, periods)

    query = """
        query GetZoneVisits($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        uniq {
                            uniques
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No visit data available in the response.")
        visit_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["uniq"]["uniques"] for item in visit_totals
        }
        return {"title": "Visits", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_views(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetZonePageViews($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        limit: 1000,
                        filter: {date_geq: $since, date_leq: $until}
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            pageViews
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No page view data available in the response.")
        view_totals = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["pageViews"] for item in view_totals
        }
        return {"title": "Views", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Network Module
def get_http_versions(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetHttpProtocols($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            clientHTTPVersionMap {
                                requests
                                clientHTTPProtocol
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No HTTP protocols data available in the response.")
        protocol_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in protocol_totals:
            for protocol in daily["sum"]["clientHTTPVersionMap"]:
                proto = protocol["clientHTTPProtocol"]
                req_count = protocol["requests"]
                results[proto] = results.get(proto, 0) + req_count
        return {"title": "HTTP Versions", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_ssl_traffic(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetSSLTraffic($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            clientSSLMap {
                                requests
                                clientSSLProtocol
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No SSL data available in the response.")
        ssl_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in ssl_totals:
            for protocol in daily["sum"]["clientSSLMap"]:
                ssl_proto = protocol["clientSSLProtocol"]
                requests = protocol["requests"]
                results[ssl_proto] = results.get(ssl_proto, 0) + requests
        return {"title": "SSL Versions", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_content_type(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetContentTypes($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        sum {
                            contentTypeMap {
                                requests
                                edgeResponseContentTypeName
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No content type data available in the response.")
        content_totals = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in content_totals:
            for content in daily["sum"]["contentTypeMap"]:
                content_type = content["edgeResponseContentTypeName"]
                requests = content["requests"]
                results[content_type] = results.get(content_type, 0) + requests
        return {"title": "Content Type", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_cached_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetCachedRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            cachedRequests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No cached requests data available in the response.")
        cached_requests = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["cachedRequests"]
            for item in cached_requests
        }
        return {"title": "Cached Requests", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_cached_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetCachedBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            cachedBytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No cached bandwidth data available in the response.")
        cached_bandwidth = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["cachedBytes"]
            for item in cached_bandwidth
        }
        return {"title": "Cached Bandwidth", "content": results, "type": "byte"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Security Module
def get_encrypted_bandwidth(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetEncryptedBandwidth($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            encryptedBytes
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No encrypted bandwidth data available in the response.")
        encrypted_bandwidth = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["encryptedBytes"]
            for item in encrypted_bandwidth
        }
        return {"title": "Encrypted Bandwidth", "content": results, "type": "byte"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


def get_encrypted_requests(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetEncryptedRequests($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            encryptedRequests
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No encrypted request data available in the response.")
        encrypted_requests = zones[0]["httpRequests1dGroups"]
        results = {
            item["dimensions"]["date"]: item["sum"]["encryptedRequests"]
            for item in encrypted_requests
        }
        return {"title": "Encrypted Requests", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response: {e}")


# Error Module
def get_fourxx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetFourXXErrors($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            responseStatusMap {
                                requests
                                edgeResponseStatus
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No 4xx error data available in the response.")
        error_stats = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in error_stats:
            date = daily["dimensions"]["date"]
            total_4xx = sum(
                status["requests"]
                for status in daily["sum"]["responseStatusMap"]
                if 400 <= int(status["edgeResponseStatus"]) < 500
            )
            results[date] = total_4xx
        return {"title": "400 Errors", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response for 4xx errors: {e}")


def get_fivexx_errors(zone_tag: str, leq_date: str, periods: int) -> dict:
    range_generated = range_generator(leq_date, periods)
    query = """
        query GetFiveXXErrors($zoneTag: String!, $since: String!, $until: String!) {
            viewer {
                zones(filter: {zoneTag_in: [$zoneTag]}) {
                    httpRequests1dGroups(
                        filter: {date_geq: $since, date_leq: $until},
                        limit: 1000
                    ) {
                        dimensions {
                            date
                        }
                        sum {
                            responseStatusMap {
                                requests
                                edgeResponseStatus
                            }
                        }
                    }
                }
            }
        }
    """
    variables = {
        "zoneTag": zone_tag,
        "since": range_generated["geq_date"][:10],
        "until": range_generated["leq_date"][:10],
    }
    response = execute_query(query, variables)
    try:
        zones = response["data"]["viewer"]["zones"]
        if not zones or not zones[0].get("httpRequests1dGroups"):
            raise ValueError("No 5xx error data available in the response.")
        error_stats = zones[0]["httpRequests1dGroups"]
        results = {}
        for daily in error_stats:
            date = daily["dimensions"]["date"]
            total_5xx = sum(
                status["requests"]
                for status in daily["sum"]["responseStatusMap"]
                if 500 <= int(status["edgeResponseStatus"]) < 600
            )
            results[date] = total_5xx
        return {"title": "500 Errors", "content": results, "type": "numeric"}
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Error processing response for 5xx errors: {e}")


# def get_account_settings(token: str, account_id: str):
#     """
#     Get basic stats from the acocunt
#     """
#     # TODO: Add dates as variables
#     url = "https://api.cloudflare.com/client/v4/graphql"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#     }
#     query = """
#         query GetAccountSettings($accountTag: string) {
#             viewer {
#                 accounts(filter: {accountTag: $accountTag}) {
#                     settings {
#                         httpRequestsOverviewAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         httpRequestsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         advancedDnsProtectionNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         dosdNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         dosdAttackAnalyticsGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         firewallEventsAdaptive {
#                             ...AccountSettings
#                             __typename
#                         }
#                         firewallEventsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         flowtrackdNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicTransitNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicTransitTunnelTrafficAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         magicFirewallNetworkAnalyticsAdaptiveGroups {
#                            ...AccountSettings
#                            __typename
#                         }
#                         spectrumNetworkAnalyticsAdaptiveGroups {
#                             ...AccountSettings
#                             __typename
#                         }
#                         __typename
#                     }
#                     __typename
#                 }
#                 __typename
#             }
#         }
#         fragment AccountSettings on Settings {
#             availableFields
#             enabled
#             maxDuration
#             maxNumberOfFields
#             maxPageSize
#             notOlderThan
#             __typename
#         }
#     """
#     variables = {
#         "accountTag": account_id,
#         "filter": {
#             "datetime_geq": "2024-12-09T22:58:00Z",
#             "datetime_leq": "2024-12-16T22:58:00Z",
#         },
#     }
#     payload = {"query": query, "variables": variables}
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         if data.get("data"):
#             print(json.dumps(data, indent=2))
#         else:
#             print(f"Error: {data.get('errors', 'Unknown error')}")
#     else:
#         print(f"HTTP Error {response.status_code}: {response.text}")
