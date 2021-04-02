from redash_toolbelt import Redash

class CustomRedash(Redash):
    def __init__(self, redash_url, api_key):
        return super().__init__(redash_url, api_key)

    def query(self, id):
        """GET api/queries"""
        return self._get(
            "api/queries/{}".format(id)
        ).json()

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

    def create_query(self, name):
        return self._post(
            'api/queries',
            json={
                'name': name,
            }
        ).json()
