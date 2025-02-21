import cloudstorage as gcs
from settings import get_bucket_name


class BucketManager(object):

    def __init__(self, bucket_name, folder_name):
        self._bucket_name = "/{0}/{1}".format(bucket_name, folder_name)

    def save(self, file_name, mode, data, mime_type=None):
        with gcs.open(file_name, mode, mime_type) as gcs_file:
            gcs_file.write(data)

    def get(self, file_name, mode="r", mime_type=None):
        gcs_file = gcs.open(file_name, mode, mime_type)

        data = gcs_file.read()

        gcs_file.close()

        return data

    def delete(self, file_name):
        try:
            gcs.delete(self.get_bucket_file_name(file_name))
        except gcs.NotFoundError:
            pass

    def delete_with_prefix(self, file_name_prefix):
        for stat in gcs.listbucket(self.get_bucket_file_name(file_name_prefix)):
            gcs.delete(stat.filename)

    def get_bucket_file_name(self, file_name):
        return "{0}/{1}".format(self._bucket_name, file_name)

    def file_exists(self, file_name):
        try:
            stat = gcs.stat(self.get_bucket_file_name(file_name))
            return stat
        except gcs.NotFoundError:
            return False

    @property
    def bucket_name(self):
        return self._bucket_name


class StateBucketManager(BucketManager):
    def __init__(self):
        BucketManager.__init__(self, 'api-blobs', 'state_strings')

    def save_state(self, file_name, state):
        object_file_name = self.get_bucket_file_name(file_name)
        self.save(object_file_name, "w", state)

    def get_state(self, file_name):
        object_file_name = self.get_bucket_file_name(file_name)
        return self.get(object_file_name)


class FileStorageBucketManager(BucketManager):
    def __init__(self):
        BucketManager.__init__(self, get_bucket_name('saved-file-storage')[1:], 'saved-files')

    def get_file_handler(self, file_name, mode="r", mime_type=None):
        object_file_name = self.get_bucket_file_name(file_name)
        return gcs.open(object_file_name, mode, mime_type)

    def save(self, file_name, state):
        object_file_name = self.get_bucket_file_name(file_name)

        return super(FileStorageBucketManager, self).save(object_file_name, "w", state)

    def get(self, file_name):
        object_file_name = self.get_bucket_file_name(file_name)

        return super(FileStorageBucketManager, self).get(object_file_name)
