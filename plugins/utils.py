import time as tm
from database import db 

STATUS = {}

class STS:
    def __init__(self, id):
        self.id = id
        self.data = STATUS
    
    def verify(self):
        return self.data.get(self.id)
    
    def store(self, from, to,  skip, limit):
        self.data[self.id] = {"FROM": from, 'TO': to, 'total_files': 0, 'skip': skip, 'limit': limit, 'fetched': skip,
                     'filtered': 0, 'deleted': 0, 'duplicate': 0, 'total': limit, 'current': skip, 'start': 0}
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.data.get(self.id)
        if not full:
           return values.get(value)
        for k, v in values.items():
            setattr(self, k, v)
        return self

    def add(self, key, value=1, time=False):
        if time:
          return self.data[self.id].update({key: tm.time()})
        self.data[self.id].update({key: self.get(key) + value, 'current': self.get('current') + value}) 
        
    async def data(self, user_id):
        k, filters = self, await db.get_filters(user_id)
        size, configs = None, await db.get_configs(user_id)
        if configs['file_size'] != 0:
            size = [configs['filesize'], configs['size_limit']]
        return configs['bot'], {'chat_id': k.FROM, 'limit': k.limit, 'off_set': k.skip, 'filters': filters,
                'media_size': size, 'extensions': configs['extensions'], 'skip_duplicate': configs['duplicate']}
        
