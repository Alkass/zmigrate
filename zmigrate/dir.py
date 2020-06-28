class Dir:
    major, minor, patch = 0, 0, 0
    def __init__(self, name=None):
        if not name:
            return
        if name.count('.') is not 2:
            raise Exception('Invalid directory name:', name)
        tokens = name.split('.')
        for i in range(len(tokens)):
            if not tokens[i].isnumeric():
                raise Exception('Invalid directory name: %s' % name)
            value = int(tokens[i])
            if i == 0:
                self.major = value
            elif i == 1:
                self.minor = value
            elif i == 2:
                self.patch = value
    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.patch)
    def toInt(self):
        return (self.major << 24) | (self.minor << 16) | self.patch
