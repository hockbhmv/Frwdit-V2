import time 

STATUS = {}

class STS:
    def __init__(self, id):
        self.id = id
        self.status = STATUS
        self.data = self.status[self.id]
        
    def store(self, From, to,  skip, limit):
        self.data = {'FROM': From, 'TO': to, 'total_files': 0, 'skip': skip, 'limit': limit, 'fetched': 0,
                     'filtered': 0, 'deleted': 0, 'duplicate': 0, 'total': 0, 'current': 0, 'start': time.time()}
        return STS(self.id)
        
    def get(self, value=None, full=False):
        values = self.status.get(self.id)
        if not full:
           return values.get(value)
        for k, v in values.items():
            setattr(value, k, v)
        return value

    def add(self, key, value=1, time=False):
        if time:
          return self.data.update({key: time})
        self.data.update({key: self.get(key) + value, 'current': self.get('current') + value}) 
