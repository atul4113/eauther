from src.mauthor.indesign.utils import convert_post_data, TextModuleIndesign


def test_convert_indesign_data_to_list_of_tuples_ids_texts():
    data = {
        "page[1][1]['id']": 'baloes_bd_8_1',
        "page[0][1]['text']": 'Mum, dad! Look, the school email.',
        "page[1][0]['id']": 'baloes_bd_9_1',
        "page[0][1]['id']": 'baloes_bd_6_1',
        "page[0][0]['id']": 'baloes_bd_5_1',
        'next': ['/mycontent/5910974510923776'],
        "page[0][0]['text']": 'Some time later\u2026',
        'space_id': '5910974510923776',
        "page[1][0]['text']": 'You open the email, Luana. \u2028It\u2019s for you!',
        "page[1][1]['text']": 'Me too!',
        'skip_editor': ['1'],
    }

    expected = [
        [TextModuleIndesign('baloes_bd_5_1', 'Some time later\u2026'), TextModuleIndesign('baloes_bd_6_1', 'Mum, dad! Look, the school email.')],
        [TextModuleIndesign('baloes_bd_9_1', 'You open the email, Luana. \u2028It\u2019s for you!'), TextModuleIndesign('baloes_bd_8_1', 'Me too!')]
    ]

    assert expected == convert_post_data(data)
