import json

class Row:
    def to_dict(self, arg):
        raise NotImplementedError

    @classmethod
    def to_json(cls, arg):
        if isinstance(arg, list):
            list_obj = [x.to_dict() for x in arg]
            return json.dumps(list_obj)
        elif isinstance(arg, cls):
            return json.dumps(arg.to_dict())


