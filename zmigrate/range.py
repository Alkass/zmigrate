from zmigrate.dir import Dir

class Range:
    first, last = None, None
    def __init__(self, raw=None):
        if not raw:
            return
        if raw.count('^') is not 1:
            raise Exception('Invalid range format: %s' % raw)
        tokens = raw.split('^')
        self.first = self.parse(tokens[0])
        self.last = self.parse(tokens[1])
    def parse(self, rawDir):
        if not rawDir or rawDir == '':
            return None
        return Dir(rawDir)
