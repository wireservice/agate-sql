from unittest.mock import patch

import agate
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

import agatesql


@pytest.fixture
def database_url(tmp_path):
    return 'sqlite:///' + (tmp_path / 'transactions.db').as_posix()


def make_table(rows):
    return agate.Table(rows, ['id', 'name'], [agate.Number(), agate.Text()])


def read_rows(url):
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            return [tuple(row) for row in connection.execute(text('SELECT id, name FROM people ORDER BY id'))]
    finally:
        engine.dispose()


@pytest.mark.parametrize('chunk_size', [None, 1])
def test_to_sql_commits_owned_connection(database_url, chunk_size):
    table = make_table([(1, 'Alice'), (2, 'Bob')])

    table.to_sql(database_url, 'people', chunk_size=chunk_size)

    assert read_rows(database_url) == [(1, 'Alice'), (2, 'Bob')]


@pytest.mark.parametrize('chunk_size', [None, 1])
def test_to_sql_rolls_back_failed_insert_and_closes_owned_connection(database_url, chunk_size):
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE people (id INTEGER UNIQUE, name TEXT)'))
        connection.execute(text("INSERT INTO people VALUES (1, 'original')"))

    connection = engine.connect()
    table = make_table([(2, 'new'), (1, 'duplicate')])
    try:
        with patch.object(agatesql.table, 'get_engine_and_connection', return_value=(engine, connection)):
            with patch.object(engine, 'dispose', wraps=engine.dispose) as dispose:
                with pytest.raises(IntegrityError):
                    table.to_sql(database_url, 'people', create=False, chunk_size=chunk_size)
                assert connection.closed
                dispose.assert_called_once_with()

        assert read_rows(database_url) == [(1, 'original')]
    finally:
        connection.close()
        engine.dispose()


@pytest.mark.parametrize('commit', [False, True])
def test_to_sql_preserves_caller_transaction(database_url, commit):
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text('CREATE TABLE people (id INTEGER, name TEXT)'))

        with engine.connect() as connection:
            transaction = connection.begin()
            table = make_table([(1, 'Alice'), (2, 'Bob')])
            table.to_sql(connection, 'people', create=False, chunk_size=1)

            assert not connection.closed
            assert transaction.is_active
            assert connection.execute(text('SELECT COUNT(*) FROM people')).scalar() == 2
            assert read_rows(database_url) == []
            if commit:
                transaction.commit()
            else:
                transaction.rollback()

        assert read_rows(database_url) == ([(1, 'Alice'), (2, 'Bob')] if commit else [])
    finally:
        engine.dispose()


def test_to_sql_preserves_caller_transaction_on_failure(database_url):
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(text('CREATE TABLE people (id INTEGER UNIQUE, name TEXT)'))

        with engine.connect() as connection:
            transaction = connection.begin()
            connection.execute(text("INSERT INTO people VALUES (1, 'caller')"))
            table = make_table([(2, 'new'), (1, 'duplicate')])
            with pytest.raises(IntegrityError):
                table.to_sql(connection, 'people', create=False, chunk_size=1)

            assert not connection.closed
            assert transaction.is_active
            assert connection.execute(text('SELECT COUNT(*) FROM people')).scalar() == 2
            transaction.rollback()

        assert read_rows(database_url) == []
    finally:
        engine.dispose()
