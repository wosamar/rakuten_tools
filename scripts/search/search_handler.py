import requests
from bs4 import BeautifulSoup
from collections import Counter


class RakutenCategory:
    def __init__(self, category_id: str, keyword: str = None):
        self.keyword = keyword or "-"
        self.category_id = category_id
        self.titles = []
        self.freq = Counter()

    def fetch_titles(self):
        url = f"https://search.rakuten.co.jp/search/mall/{self.keyword}/{self.category_id}/"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        self.titles = [h2.get_text(strip=True) for h2 in soup.select("div.searchResults div.dui-card h2")
                       if "[PR]" not in h2.get_text()]
        return self.titles

    def compute_frequency(self):
        all_text = " ".join(self.titles)
        self.freq = Counter(all_text.split())
        return self.freq


def display_titles(self):
    print(f"{'No.':<4} Title")
    for i, t in enumerate(category.titles, 1):
        print(f"{i:<4} {t}")


def display_freq(self, top_n=20):
    print(f"\n{'Word':<15} Count")
    for word, count in category.freq.most_common(top_n):
        print(f"{word:<15} {count}")


if __name__ == '__main__':
    # TODO:多關鍵字檢索/去重複
    category = RakutenCategory("215479")
    category.fetch_titles()
    category.compute_frequency()

    category.display_titles()
    category.display_freq()
