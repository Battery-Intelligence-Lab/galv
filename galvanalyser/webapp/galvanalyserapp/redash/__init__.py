from redash_toolbelt import Redash

def CustomRedash(Redash):

    def create_group(self, name):
        return self._post('api/groups', json={'name': name}).json()

    def create_data_source(self, name, type, options):
        return self._post(
            'api/data_sources',
            json={
                'name': name,
                'options': options,
                'type': type,
            }).json()

    def create_query(self, name, data_source_id, query_str,
                     description=None, schedule=60, options=None):
        return self._post(
            'api/queries',
            json={
                'name': name,
                'data_source_id': data_source_id,
                'query': query_str,
                'description': description,
                'schedule': str(schedule),
                'options': options,
            }
        ).json()


def create_group(config, name):
    redash = Redash(
        config['db_conf']['redash_url'],
        config['db_conf']['redash_api_key']
    )

    redash.create_group(group)


def create_data_source(config, user, pwd):
    redash.create_data_source(
        group, 'PostgreSQL',
        {
            'user': user,
            'password': pwd,
            'host': config['db_conf']['database_host'],
            'port': config['db_conf']['database_port'],
            'dbname': config['db_conf']['database_name'],
        }
    )
