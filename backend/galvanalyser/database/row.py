import json

class Row:
    def to_dict(self, arg, conn):
        raise NotImplementedError

    @classmethod
    def to_json(cls, arg, conn):
        if isinstance(arg, list):
            list_obj = [x.to_dict(conn) for x in arg]
            return json.dumps(list_obj)
        elif isinstance(arg, cls):
            return json.dumps(arg.to_dict(conn))


