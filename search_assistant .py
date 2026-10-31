"""
Internet Search Assistant - Python Mini Project
Submitted by : Keshav Saini (UID: 25BCD10101)
Submitted to : Mrs. Preeti, Assistant Professor

A command-line tool that searches the internet using free public APIs
(Wikipedia + DuckDuckGo), shows readable results in the terminal,
opens links in the browser and keeps a search history in a JSON file.
"""

import json
import os
import textwrap
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

import requests

HISTORY_FILE = "search_history.json"
HEADERS = {"User-Agent": "InternetSearchAssistant/1.0 (student mini project)"}
WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"
DDG_API = "https://api.duckduckgo.com/"


def banner():
    print("=" * 56)
    print("        INTERNET SEARCH ASSISTANT  (Python)")
    print("=" * 56)


def menu():
    print("\n1. Search Wikipedia")
    print("2. Quick answer (DuckDuckGo)")
    print("3. Open a Google search in browser")
    print("4. View search history")
    print("5. Clear search history")
    print("0. Exit")
    return input("\nEnter your choice: ").strip()


# ---------------------------------------------------------------- history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(query, source):
    history = load_history()
    history.append({
        "query": query,
        "source": source,
        "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def show_history():
    history = load_history()
    if not history:
        print("\nNo searches yet.")
        return
    print(f"\n{'No.':<5}{'Time':<22}{'Source':<12}Query")
    print("-" * 56)
    for i, item in enumerate(history, 1):
        print(f"{i:<5}{item['time']:<22}{item['source']:<12}{item['query']}")


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    print("\nHistory cleared.")


# ------------------------------------------------------------- searching
def wiki_search(query):
    params = {"action": "query", "list": "search", "srsearch": query,
              "srlimit": 5, "format": "json"}
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except requests.RequestException as err:
        print(f"\nNetwork error: {err}")
        return
    results = r.json()["query"]["search"]
    if not results:
        print("\nNo results found.")
        return
    save_history(query, "Wikipedia")
    print(f"\nTop {len(results)} results for '{query}':\n")
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item['title']}")
    pick = input("\nEnter result number to read summary (Enter to skip): ")
    if pick.isdigit() and 1 <= int(pick) <= len(results):
        wiki_summary(results[int(pick) - 1]["title"])


def wiki_summary(title):
    url = WIKI_SUMMARY + quote_plus(title.replace(" ", "_"))
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
    except requests.RequestException as err:
        print(f"\nNetwork error: {err}")
        return
    data = r.json()
    print("\n" + "-" * 56)
    print(data["title"].upper())
    print("-" * 56)
    print(textwrap.fill(data["extract"], width=56))
    link = data["content_urls"]["desktop"]["page"]
    print(f"\nRead more: {link}")
    if input("Open in browser? (y/n): ").lower() == "y":
        webbrowser.open(link)


def quick_answer(query):
    params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
    try:
        r = requests.get(DDG_API, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as err:
        print(f"\nNetwork error: {err}")
        return
    save_history(query, "DuckDuckGo")
    answer = data.get("AbstractText") or data.get("Answer")
    if answer:
        print("\n" + textwrap.fill(answer, width=56))
        print(f"\nSource: {data.get('AbstractSource', 'DuckDuckGo')}")
        print(f"Link  : {data.get('AbstractURL', '-')}")
    else:
        print("\nNo instant answer found. Try option 1 or 3.")


def google_search(query):
    save_history(query, "Google")
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))
    print("\nOpening Google in your browser...")


# ------------------------------------------------------------------ main
def main():
    banner()
    while True:
        choice = menu()
        if choice == "1":
            wiki_search(input("Enter search topic: ").strip())
        elif choice == "2":
            quick_answer(input("Enter your question: ").strip())
        elif choice == "3":
            google_search(input("Enter search text: ").strip())
        elif choice == "4":
            show_history()
        elif choice == "5":
            clear_history()
        elif choice == "0":
            print("\nThank you for using Internet Search Assistant!")
            break
        else:
            print("\nInvalid choice, please try again.")


if __name__ == "__main__":
    main()
