import enum
import psycopg2

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

    def validate_password(self, password):
        try:
            app.config['GET_DATABASE_CONN_FOR_USER'](
                self.username, password
            )
            return True
        except psycopg2.OperationalError:
            return False

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
            if member_of == 'normal_user':
                role = UserRoles.ReadOnly
            elif member_of == 'harvester':
                role = UserRoles.Harvester
            else:
                role = None
            return cls(username, role)
