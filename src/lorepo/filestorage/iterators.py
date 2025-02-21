class GcsIterator(object):
    def __init__(self, gcs_iterator):
        self.iter = gcs_iterator

    def __iter__(self):
        return self

    def __next__(self):
        try:
            obj = next(self.iter)
            return obj
        except StopIteration:
            self.iter.close()
            raise StopIteration
