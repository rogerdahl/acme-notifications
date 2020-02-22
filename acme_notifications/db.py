import pathlib
import sqlite3

import flask


def get_db():
    db = getattr(flask.g, "_database", None)
    if db is None:
        app = flask.current_app
        instance_path = app.instance_path
        db_path = pathlib.Path(instance_path, app.config["DATABASE"])
        db = flask.g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    # By default, sqlite3 forces a disk sync (fsync syscall) after each commit,
    # which is very slow, especially on the RPi. Turning the sync off increases
    # the chance of db corruption but seems unlikely with the rare DB updates
    # performed by this app.
    # db.execute("PRAGMA synchronous=OFF")
    return db


def query_db(query, args=(), one=False, commit=False):
    cur = get_db().execute(query, args)
    if commit:
        get_db().commit()
        cur.close()
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def close_db():
    db = getattr(flask.g, "_database", None)
    if db is not None:
        db.close()


def add_message(title_str, body_str):
    query_db(
        """
        insert into notifications (title, body)
        values (?, ?);
        """,
        (title_str, body_str),
        one=True,
        commit=True,
    )


# auth_user


def set_user_access_token(authed_user_id, access_token):
    flask.current_app.logger.error((authed_user_id, access_token))
    query_db(
        """
      replace into auth_user (authed_user_id, access_token) values(?, ?)  
    """,
        (authed_user_id, access_token),
        one=True,
        commit=True,
    )


def get_user_access_token(authed_user_id):
    row = query_db(
        """
        select access_token from auth_user where authed_user_id=?
    """,
        (authed_user_id,),
        one=True,
    )
    if row is not None:
        return row["access_token"]


# user


def set_user_info(user_id, display_name):
    query_db(
        """
      replace into user_info (user_id, display_name) values(?, ?)  
    """,
        (user_id, display_name),
        one=True,
        commit=True,
    )


def get_user_info(user_id):
    row = query_db(
        """
      select display_name from user_info where user_id = ?
    """,
        (user_id,),
        one=True,
    )
    if row is not None:
        return row["display_name"]
