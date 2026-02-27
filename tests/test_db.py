import pytest
from unittest.mock import MagicMock, patch
from core.db import Neo4jDB


def test_neo4j_db_init_creates_constraints():
    with patch("core.db.GraphDatabase") as mock_gdb:
        mock_driver = MagicMock()
        mock_gdb.driver.return_value = mock_driver
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        db = Neo4jDB(uri="bolt://localhost", username="neo4j", password="test")
        db.init_schema()
        assert mock_session.run.called


def test_upsert_viewer_calls_merge():
    with patch("core.db.GraphDatabase") as mock_gdb:
        mock_driver = MagicMock()
        mock_gdb.driver.return_value = mock_driver
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        db = Neo4jDB(uri="bolt://localhost", username="neo4j", password="test")
        db.upsert_viewer("testuser", donated=5.0)
        assert mock_session.run.called
