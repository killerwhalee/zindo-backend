import requests
import environ
from django.conf import settings

env = environ.Env()
env.read_env(settings.BASE_DIR / ".env")


def get_subject(title):
    """Get subject from book title.

    This function is currently hard-coded.
    It looks some keyword inside book title and decide its subject.

    Use this function at your own risk of:
    - Malfunction may happen if keyword pool is too shallow.
    - Its time complexity is O(n^2), which can be time-consuming.

    """

    # keyword pool
    pool = {
        "국어": ["국어", "독해", "문법", "읽기", "쓰기", "한글"],
        "수학": ["수학", "연산", "계산"],
    }

    # Run keyword search for each subject.
    for subject, keywords in pool.items():
        for keyword in keywords:
            if keyword in title:
                return subject

    return None


def search_book(isbn):
    """Search book using given isbn.

    Using Naver search API, finds book with given isbn.
    Only the first result is returned.

    Note - Actually this works with other keywords.
    But use only isbn for accuracy.

    """

    # Initialize url with headers
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": env("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": env("NAVER_CLIENT_SECRET"),
    }

    # Run requests to get response, then fetch search results
    try:
        response = requests.get(url, headers=headers, params={"query": isbn})
        items = response.json().get("items", [])

    # Return empty dict if error occurred
    except (requests.RequestException, ValueError, KeyError):
        return {}

    # Return empty dict if no books were found
    if not items:
        return {}

    # Get first data from items and serialize
    item = items[0]
    title = item.get("title", "")
    subject = get_subject(title) or "없음"
    isbn = item.get("isbn", "")
    image = item.get("image", "")

    return {
        "object": "textbook",
        "id": None,
        "name": title,
        "subject": subject,
        "isbn": isbn,
        "image": image,
    }
