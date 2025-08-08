import requests


def make_request():
    requests.get(
        "https://oldschool.runescape.wiki/api.php",
        headers={"user-agent": "nid (@bouk on discord)"},
    )


if __name__ == "__main__":
    print("poj")
