# Encodes datetime and hashes

import json
from datetime import datetime


def stringify(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    if hasattr(obj, 'hexdigest'):
        return obj.hexdigest()


class SmartJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        out = stringify(obj)
        if out:
            return out

        return json.JSONEncoder.default(self, obj)