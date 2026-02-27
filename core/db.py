"""Neo4j knowledge graph driver and schema management."""
from __future__ import annotations
from neo4j import GraphDatabase, Driver

SCHEMA_QUERIES = [
    "CREATE CONSTRAINT viewer_username IF NOT EXISTS FOR (v:Viewer) REQUIRE v.username IS UNIQUE",
    "CREATE CONSTRAINT stream_id IF NOT EXISTS FOR (s:Stream) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
]


class Neo4jDB:
    def __init__(self, uri: str, username: str, password: str) -> None:
        self._driver: Driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self) -> None:
        self._driver.close()

    def init_schema(self) -> None:
        with self._driver.session() as session:
            for query in SCHEMA_QUERIES:
                session.run(query)

    def upsert_viewer(self, username: str, donated: float = 0.0, sub_tier: int = 0) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MERGE (v:Viewer {username: $username})
                ON CREATE SET v.first_seen = datetime(), v.total_donated = $donated,
                              v.sub_tier = $sub_tier, v.message_count = 0
                ON MATCH SET  v.total_donated = v.total_donated + $donated,
                              v.sub_tier = CASE WHEN $sub_tier > 0 THEN $sub_tier ELSE v.sub_tier END
                """,
                username=username, donated=donated, sub_tier=sub_tier,
            )

    def get_viewer(self, username: str) -> dict | None:
        with self._driver.session() as session:
            result = session.run(
                "MATCH (v:Viewer {username: $username}) RETURN v",
                username=username,
            )
            record = result.single()
            return dict(record["v"]) if record else None

    def create_stream_node(self, stream_id: str) -> None:
        with self._driver.session() as session:
            session.run(
                "MERGE (s:Stream {id: $id}) ON CREATE SET s.date = datetime(), s.total_revenue = 0.0",
                id=stream_id,
            )

    def record_donation(self, username: str, stream_id: str, amount: float) -> None:
        with self._driver.session() as session:
            session.run(
                """
                MATCH (v:Viewer {username: $username})
                MATCH (s:Stream {id: $stream_id})
                MERGE (v)-[r:DONATED]->(s)
                ON CREATE SET r.amount = $amount, r.timestamp = datetime()
                ON MATCH SET  r.amount = r.amount + $amount
                """,
                username=username, stream_id=stream_id, amount=amount,
            )
