from math import floor
from pathlib import Path
import json
from typing import Any

from rapidfuzz import fuzz

def pretty_print_dict(dictionary: dict[Any]):
    print(json.dumps(dictionary, indent=4))

class DiscordAnalysis:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.messages = json.load(file_path.open())

    def get_all_attachments(self) -> list[str]:
        attachments = []
        for key, value in self.messages.items():
            attachments.extend(value["attachments"])
        return attachments

    def get_profanities(self, threshold: float = 70, min_len: int = 2) -> dict[str, list]:
        with open(Path("data/profanities.txt"), "r") as f:
            swears = [line.strip() for line in f]

        profanity_map = {swear: [] for swear in swears}

        for idx, (msg_id, message) in enumerate(self.messages.items(), 1):
            content = message.get("content", "")
            print(f"Processing message {idx} of {len(self.messages)}")

            if len(content) < min_len:
                continue

            for swear in swears:
                for word in content.split():
                    if fuzz.ratio(word, swear) >= threshold:
                        profanity_map[swear].append(message)
                        break

        return profanity_map

    def fuzzy_search_messages(self, query: str, threshold: float = 75) -> list[dict]:
        messages = list()
        for idx, message in self.messages.items():
            if fuzz.partial_ratio(query, message.get("content")) >= threshold:
                messages.append(message)
        return messages


if __name__ == "__main__":
    # da = DiscordAnalysis(Path(r"D:\python\discord-scraper\src\data\sussy1287640764192522243.json"))
    da = DiscordAnalysis(Path(r"D:\python\discord-scraper\src\data\1530222266611404872.json"))
    # print(da.get_all_attachments())
    # pretty_print_dict(da.get_profanities())
    # pretty_print_dict(da.fuzzy_search_messages("hello"))