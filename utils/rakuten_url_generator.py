import urllib.parse


def generate_rakuten_search_url(search_string: str) -> str:
    """
    Generates a Rakuten search URL for a given search string.

    Args:
        search_string: The string to search for on Rakuten.

    Returns:
        A formatted Rakuten search URL.
    """
    base_url = "https://search.rakuten.co.jp/search/mall/"
    shop_id = "403482"
    encoded_search_string = urllib.parse.quote(search_string, safe='')
    return f"{base_url}{encoded_search_string}/?sid={shop_id}"


if __name__ == '__main__':
    for i in [5, 10, 15, 20]:
        print(generate_rakuten_search_url(f"10/24から{i}倍ポイント"))
