import enum
import psycopg2
import json

from flask import current_app as app

class UserRoles(str, enum.Enum):
   ReadOnly = 'RO'
   Harvester = 'H'

class User():
    def __init__(self, username, role):
        self.username = username
        if role is None:
            self.role = None
        else:
            self.role = UserRoles(role)

    def __repr__(self):
        return 'User({}, {})'.format(
            self.username, self.role
        )

    def to_dict(self):
        return {
            'username': self.username,
            'role': self.role,
        }

    @classmethod
    def to_json(cls, arg):
        if isinstance(arg, list):
            list_obj = [x.to_dict() for x in arg]
            return json.dumps(list_obj)
        elif isinstance(arg, cls):
            return json.dumps(arg.to_dict())

    @classmethod
    def from_json(cls, json_str):
        user_dict = json.loads(json_str)
        return cls(user_dict['username'], user_dict['role'])

    def validate_password(self, password):
        try:
            app.config['GET_DATABASE_CONN_FOR_USER'](
                self.username, password
            )
            return True
        except psycopg2.OperationalError:
            return False

    @classmethod
    def all(cls):
        conn = app.config['GET_DATABASE_CONN_FOR_SUPERUSER']()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT a.rolname, b.rolname "
                "FROM pg_roles a "
                "INNER JOIN ( "
                "   SELECT c.member, d.rolname "
                "   FROM pg_auth_members c "
                "   INNER JOIN pg_roles d "
                "   ON c.roleid = d.oid "
                ") b ON a.oid = b.member "
                "WHERE b.rolname in ('normal_user', 'harvester'); "
            )
            records = cur.fetchall()
            return [
                cls(
                    username=result[0],
                    role=cls.get_role_from_member_of(result[1]),
                )
                for result in records
            ]

    @classmethod
    def get_role_from_member_of(cls, member_of):
        if member_of == 'normal_user':
            role = UserRoles.ReadOnly
        elif member_of == 'harvester':
            role = UserRoles.Harvester
        else:
            role = None
        return role

    @classmethod
    def get(cls, username):
        conn = app.config['GET_DATABASE_CONN_FOR_SUPERUSER']()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT b.rolname "
                "FROM pg_roles a "
                "INNER JOIN ( "
                "   SELECT c.member, d.rolname "
                "   FROM pg_auth_members c "
                "   INNER JOIN pg_roles d "
                "   ON c.roleid = d.oid "
                ") b ON a.oid = b.member "
                "WHERE a.rolname = (%s); ",
                [username]
            )
            result = cur.fetchone()
            if result is None:
                member_of = None
            else:
                member_of = result[0]
            role = cls.get_role_from_member_of(member_of)
            return cls(username, role)
