class StubReader(object):
    def seek(self, offset):
        pass
    def read(self, length):
        return 'a' * length
    def close(self):
        pass