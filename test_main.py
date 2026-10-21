from fastapi.testclient import TestClient
from typing import Any
from unittest.mock import call
from unittest.mock import create_autospec
import sqlite3


import main


client = TestClient(main.app)


def create_sqlite3_mock_connection_and_cursor(
        cursor_fetchall_returns: list[Any] = [],
        cursor_fetchone_returns: Any = None,
        cursor_lastrowid: int | None = None):
    """Create autospecced sqlite3 connection and cursor mocks, wired together.

    Args:
        cursor_fetchall_returns: Value returned by cursor.fetchall().
            A list of rows; pass [] for no results.
        cursor_fetchone_returns: Value returned by cursor.fetchone().
            A single row; pass None for no result.
        cursor_lastrowid: Value of cursor.lastrowid—e.g., the id of the
            row just inserted.

    Returns:
        A ``(mock_connection, mock_cursor)`` tuple.
    """
    mock_connection = create_autospec(
        sqlite3.Connection, spec_set=True, instance=True)

    mock_cursor = create_autospec(sqlite3.Cursor, spec_set=True, instance=True)
    mock_cursor.fetchall.return_value = cursor_fetchall_returns
    mock_cursor.fetchone.return_value = cursor_fetchone_returns
    if cursor_lastrowid is not None:
        mock_cursor.lastrowid = cursor_lastrowid

    mock_connection.cursor.return_value = mock_cursor

    return (mock_connection, mock_cursor)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Notes API is running"


def test_get_notes(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchall_returns=[])
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == []
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM notes ORDER BY id")


def test_get_note(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns={"id": 100, "title": "foo", "text": "bar"})
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.get("/notes/100")

    assert response.status_code == 200
    assert response.json() == {"id": 100, "title": "foo", "text": "bar"}
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM notes WHERE id = ?", (100,))


def test_get_note_unknown_id(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns=None)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.get("/notes/100")

    assert response.status_code == 404
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM notes WHERE id = ?", (100,))


def test_create_note(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_lastrowid=19820216)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.post("/notes", json={"title": "foo", "text": "bar"})

    assert response.status_code == 201
    assert response.json() == {"id": 19820216, "title": "foo", "text": "bar"}
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO notes (title, text) VALUES (?, ?)",
        ("foo", "bar"))


def test_update_note(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns={"id": 100, "title": "foo", "text": "bar"})
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.patch("/notes/100", json={"text": "baz"})

    assert response.status_code == 200
    assert response.json() == {"id": 100, "title": "foo", "text": "baz"}
    assert mock_cursor.execute.call_args_list == [
        call("SELECT * FROM notes WHERE id = ?", (100,)),
        call("UPDATE notes SET title = ?, text = ? WHERE id = ?",
            ("foo", "baz", 100))]


def test_update_note_unknown_id(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns=None)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.patch("/notes/100", json={"text": "baz"})

    assert response.status_code == 404
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM notes WHERE id = ?", (100,))

def test_delete_note(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns={"id": 100, "title": "foo", "text": "bar"})
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.delete("/notes/100")

    assert response.status_code == 200
    assert mock_cursor.execute.call_args_list == [
        call("SELECT * FROM notes WHERE id = ?", (100,)),
        call("DELETE FROM notes WHERE id = ?", (100,))]


def test_delete_note_unknown_id(monkeypatch):
    (mock_connection, mock_cursor) = create_sqlite3_mock_connection_and_cursor(
        cursor_fetchone_returns=None)
    monkeypatch.setattr(
        sqlite3, "connect", lambda *args, **kwargs: mock_connection)

    response = client.delete("/notes/100")

    assert response.status_code == 404
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM notes WHERE id = ?", (100,))
