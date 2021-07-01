import psycopg2
import os
import hashlib
from validate_email import validate_email
import json
from galvanalyser.database import Row


def verify_email(email):
    return validate_email(
        email_address=email,
        check_regex=True, check_mx=False,
        from_address='my@from.addr.ess',
        helo_host='my.host.name',
        smtp_timeout=10, dns_timeout=10,
        use_blacklist=True, debug=False
    )


class UserRow(Row):
    def __init__(self, username, email, password=None, salt=None, id_=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.email = email
        self.id = id_

    @staticmethod
    def create(username, password, email):
        # limit password length:
        # https://docs.python.org/3/library/hashlib.html#key-derivation
        if len(password) > 1024:
            raise RuntimeError(
                'password must be less than 1024 character in length'
            )
        if not verify_email(email):
            raise RuntimeError(
                'email address "{}" not valid'.format(email)
            )
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return UserRow(
            username, email,
            password=key.hex(), salt=salt.hex()
        )

    def validate_password(self, password):
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            bytes.fromhex(self.salt),
            100000
        )
        return new_key.hex() == self.password

    @staticmethod
    def from_json(json_str):
        user_dict = json.loads(json_str)
        return UserRow(
            username=user_dict['username'],
            email=user_dict['email'],
            id_=user_dict['id'],
        )

    def to_dict(self):
        # dont expose salt or hashed password
        obj = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }
        return obj

    def insert(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_data.user "
                "(username, password, salt, email) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                [self.username, self.password, self.salt,
                 self.email],
            )
            self.id = cursor.fetchone()[0]

    def update(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "UPDATE user_data.user SET "
                    "username = (%s) "
                    "password = (%s) "
                    "salt = (%s) "
                    "email = (%s) "
                    "WHERE id=(%s)"
                ),
                [self.username, self.password, self.salt, self.email],
            )

    def delete(self, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "DELETE FROM user_data.user "
                    "WHERE id=(%s)"
                ),
                [self.id],
            )

    @staticmethod
    def select_from_id(id_, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT username, email, password, salt "
                    "FROM user_data.user WHERE "
                    "id=(%s)"
                ),
                [id_],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return UserRow(
                id_=id_,
                username=result[0],
                email=result[1],
                password=result[2],
                salt=result[3],
            )

    @staticmethod
    def select_from_username(username, conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, email, password, salt "
                    "FROM user_data.user WHERE "
                    "username=(%s)"
                ),
                [username],
            )
            result = cursor.fetchone()
            if result is None:
                return None
            return UserRow(
                id_=result[0],
                username=username,
                email=result[1],
                password=result[2],
                salt=result[3],
            )


    @staticmethod
    def all(conn):
        with conn.cursor() as cursor:
            cursor.execute(
                (
                    "SELECT id, username, email, password, salt "
                    "FROM user_data.user"
                ),
            )
            records = cursor.fetchall()
            return [
                UserRow(
                    id_=result[0],
                    username=result[1],
                    email=result[2],
                    password=result[3],
                    salt=result[4],
                )
                for result in records
            ]
