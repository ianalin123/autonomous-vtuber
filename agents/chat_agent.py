"""Chat agent — intelligent message triage and response dispatch."""
from core.interfaces import ChatMessage, EventType

SPAM_PATTERNS = ["http://", "https://", "follow4follow", "sub4sub"]


class ChatAgent:
    def classify(self, msg: ChatMessage) -> str:
        if msg.is_donation:
            return "donation"
        if msg.is_sub:
            return "subscription"
        if any(p in msg.text.lower() for p in SPAM_PATTERNS):
            return "spam"
        if msg.text.startswith("!") or msg.text.endswith("?"):
            return "question"
        return "chat"

    def should_respond(self, msg: ChatMessage) -> bool:
        classification = self.classify(msg)
        return classification in ("donation", "subscription", "question")

    def format_donation_response(self, msg: ChatMessage) -> str:
        amount = f"${msg.donation_amount:.2f}"
        return f"OH WAIT — {msg.username} just dropped {amount}?? okay but ACTUALLY though thank you so much {msg.username} that literally made my day"
