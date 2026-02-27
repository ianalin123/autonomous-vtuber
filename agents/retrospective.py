"""Post-stream retrospective — analytics summary and bandit weight updates."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StreamSummary:
    stream_id: str
    duration_minutes: float
    peak_viewers: int
    total_revenue: float
    revenue_per_hour: float
    top_activities: list[str]
    chat_messages: int
    engagement_score: float


class StreamRetrospective:
    def __init__(self, db, bandit) -> None:
        self._db = db
        self._bandit = bandit

    def build_summary(
        self,
        stream_id: str,
        duration_minutes: float,
        peak_viewers: int,
        total_revenue: float,
        top_activities: list[str],
        chat_messages: int,
    ) -> StreamSummary:
        hours = duration_minutes / 60 or 1
        engagement = min((chat_messages / duration_minutes) / 100 * 100, 100) if duration_minutes else 0
        return StreamSummary(
            stream_id=stream_id,
            duration_minutes=duration_minutes,
            peak_viewers=peak_viewers,
            total_revenue=total_revenue,
            revenue_per_hour=round(total_revenue / hours, 2),
            top_activities=top_activities,
            chat_messages=chat_messages,
            engagement_score=round(engagement, 1),
        )

    def generate_recommendations(self, summary: StreamSummary) -> list[str]:
        recs: list[str] = []
        if summary.revenue_per_hour < 10:
            recs.append("Set a donation goal early in the stream to prime giving behavior")
        if summary.engagement_score < 30:
            recs.append("Chat velocity was low — try more direct questions and polls")
        if "idle" in summary.top_activities:
            recs.append("Replace idle time with q_and_a segments — high engagement, low effort")
        if summary.peak_viewers > 200 and summary.total_revenue < 20:
            recs.append("High viewer count but low revenue — introduce subscription perks mention")
        if not recs:
            recs.append("Stream performed well — maintain current content mix")
        return recs

    def update_bandit(self, summary: StreamSummary) -> None:
        if not self._bandit:
            return
        reward = min(summary.revenue_per_hour / 50, 1.0)
        for activity in summary.top_activities:
            try:
                from core.bandit import Action
                action = Action(activity)
                self._bandit.update(action, reward=reward)
            except ValueError:
                pass

    def format_report(self, summary: StreamSummary) -> str:
        recs = self.generate_recommendations(summary)
        lines = [
            f"=== Stream Retrospective: {summary.stream_id} ===",
            f"Duration:      {summary.duration_minutes:.0f} min",
            f"Peak viewers:  {summary.peak_viewers}",
            f"Revenue:       ${summary.total_revenue:.2f} (${summary.revenue_per_hour:.2f}/hr)",
            f"Chat messages: {summary.chat_messages}",
            f"Engagement:    {summary.engagement_score:.1f}/100",
            f"Top activities:{', '.join(summary.top_activities)}",
            "",
            "Recommendations:",
            *[f"  - {r}" for r in recs],
        ]
        return "\n".join(lines)

    def save_to_neo4j(self, summary: StreamSummary) -> None:
        if not self._db:
            return
        self._db.create_stream_node(summary.stream_id)
