# coding=utf-8
import pytest
from src.libraries.utility.BucketManager import BucketManager
from mock import patch, MagicMock


@patch('libraries.utility.BucketManager.gcs.open')
class TestBucketManagerSaving(object):
    @pytest.mark.parametrize('input_data', [
        'superD234l.23/4.23/423][;23423,.4>?>":}{}{ata',
        '',
        'asdasdasdasd',
        '21312e21d12d1d',
        'zażółć_gęślą_jaźń',
        """/* TEXT COLORING */.addon_Text_Coloring{
    color: #424242;
    line-height: 58px;
}""",
        chr(226),
        'Ý╠ß┐.'
    ])
    def test_saving_to_bucket_manager_will_save_to_gcs(self, _open_mock, input_data):
        file_mock = MagicMock()
        file_object = _open_mock.return_value.__enter__.return_value = file_mock
        manager = BucketManager('a', 'b')

        manager.save('file_name', 'r', input_data)

        _open_mock.assert_called_once_with('file_name', 'r', None)
        file_object.write.assert_called_once_with(input_data)