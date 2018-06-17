# Encodes datetime and hashes

import json
from datetime import datetime


class SmartJSONEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        if hasattr(obj, 'hexdigest'):
            return obj.hexdigest()

        return json.JSONEncoder.default(self, obj)