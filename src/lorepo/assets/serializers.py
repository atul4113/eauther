import calendar
from lorepo.mycontent.models import Asset
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer


class AssetsSerializer (ModelSerializer):
    created_date = SerializerMethodField()
    size = SerializerMethodField()

    class Meta:
        model = Asset
        fields = ('href', 'content_type', 'title', 'file_name', 'created_date', 'size')

    def get_created_date(self, asset):
        uploaded_file = self.context.get('file')

        if uploaded_file and uploaded_file.created_date:
            return calendar.timegm(uploaded_file.created_date.timetuple()) * 1000

        return None

    def get_size(self, asset):
        uploaded_file = self.context.get('file')

        if uploaded_file:
            return uploaded_file.get_size()

        return None