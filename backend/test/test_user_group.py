from galvanalyser_test_case import GalvanalyserTestCase
from galvanalyser.database.user_data import (
    Group, User
)
from sqlalchemy import select
import datetime


class TestUserGroup(GalvanalyserTestCase):
    def test_admin_group_exists(self):
        with self.Session() as session:
            admin = session.execute(
                select(Group).where(Group.groupname == 'admin')
            ).one()[0]
            self.assertEqual(admin.groupname, 'admin')

    def test_relationships(self):
        with self.Session() as session:
            # create user
            user = User(
                username='tester',
                email='test@gmail.com',
            )

            # create group
            group = Group(
                groupname='everyone',
            )

            # get admin group
            admin = session.execute(
                select(Group).where(Group.groupname == 'admin')
            ).one()[0]

            # add to groups
            user.groups.append(group)
            user.groups.append(admin)

            session.add_all([user, group])
            session.commit()

            # get back user
            user = session.execute(
                select(User).where(User.username == 'tester')
            ).one()[0]
            self.assertEqual(len(user.groups), 2)
