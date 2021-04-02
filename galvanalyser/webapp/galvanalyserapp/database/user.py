import flask_login


class User(flask_login.UserMixin):
    def __init__(self, name, email, groups, details, conn):
        self.name = name
        self.email = email
        self.groups = groups
        self.details = details
        self.conn = conn

    def __repr__(self):
        return 'User({}, {}, {}, {})'.format(
            self.name, self.email, self.groups,
            self.details
        )

    @classmethod
    def get(cls, _id, conn):
        with conn.cursor() as cur:
            cur.execute(
                (
                    "SELECT name, email, groups, details "
                    "FROM public.users ",
                    "WHERE id=(%s) "
                ),
                [_id],
            )
            result = cur.fetchone()

            if result is None:
                return None

            return User(
                name=result[0],
                email=result[1],
                groups=result[2],
                details=result[4],
                conn=conn,
            )



