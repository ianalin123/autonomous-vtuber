"""Chat agent — intelligent message triage, Neo4j viewer lookup, donor personalization."""
from __future__ import annotations
from core.interfaces import ChatMessage

SPAM_PATTERNS = ["follow4follow", "sub4sub", "http://", "https://", "discord.gg/", "bit.ly/"]

DONATION_RESPONSES_NEW = [
    "OH WAIT — {username} just dropped ${amount}?? okay but ACTUALLY though thank you so much {username} that literally made my day",
    "{username} came in with ${amount} and I am not normal about this. THANK YOU {username}!!",
    "chat did you see that?? {username} with ${amount}?? I'm— okay. okay. thank you {username} genuinely",
]

DONATION_RESPONSES_RETURNING = [
    "{username} is BACK and they brought ${amount} with them?? {username} you've given so much already, thank you literally every time",
    "okay chat {username} has donated ${amount} and they've been here since forever — {username} you are literally the reason I do this",
]

SUB_RESPONSES = {
    1: "{username} just subscribed!! welcome to the chaos {username} we're so glad you're here",
    2: "{username} with the Tier 2?? {username} you did NOT have to do that but I am so happy you did",
    3: "TIER THREE?? {username} I am literally going to cry. {username} thank you so much oh my god",
}


class ChatAgent:
    def __init__(self, db) -> None:
        self._db = db
        self._response_index = 0

    def classify(self, msg: ChatMessage) -> str:
        if msg.is_donation:
            return "donation"
        if msg.is_sub:
            return "subscription"
        if any(p in msg.text.lower() for p in SPAM_PATTERNS):
            return "spam"
        if msg.text.endswith("?") or msg.text.startswith("!"):
            return "question"
        return "chat"

    def should_respond(self, msg: ChatMessage) -> bool:
        return self.classify(msg) in ("donation", "subscription", "question")

    def get_viewer_history(self, username: str) -> dict | None:
        if self._db is None:
            return None
        return self._db.get_viewer(username)

    def format_donation_response(self, msg: ChatMessage, viewer_history: dict | None) -> str:
        amount = f"{msg.donation_amount:.2f}"
        is_returning = viewer_history and viewer_history.get("total_donated", 0) > msg.donation_amount

        templates = DONATION_RESPONSES_RETURNING if is_returning else DONATION_RESPONSES_NEW
        template = templates[self._response_index % len(templates)]
        self._response_index += 1
        return template.format(username=msg.username, amount=amount)

    def format_sub_response(self, msg: ChatMessage) -> str:
        tier = msg.sub_tier or 1
        template = SUB_RESPONSES.get(tier, SUB_RESPONSES[1])
        return template.format(username=msg.username)

    def process(self, msg: ChatMessage) -> str | None:
        classification = self.classify(msg)
        if classification == "spam":
            return None
        if classification == "donation":
            history = self.get_viewer_history(msg.username)
            return self.format_donation_response(msg, history)
        if classification == "subscription":
            return self.format_sub_response(msg)
        return None
