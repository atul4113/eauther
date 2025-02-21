from src.mauthor.indesign.utils import convert_post_data, TextModuleIndesign


def test_convert_indesign_data_to_list_of_tuples_ids_texts():
    data = {
        u"page[1][1]['id']": u'baloes_bd_8_1',
        u"page[0][1]['text']": u'Mum, dad! Look, the school email.',
        u"page[1][0]['id']": u'baloes_bd_9_1',
        u"page[0][1]['id']": u'baloes_bd_6_1',
        u"page[0][0]['id']": u'baloes_bd_5_1',
        u'next': [u'/mycontent/5910974510923776'],
        u"page[0][0]['text']": u'Some time later\u2026',
        u'space_id': u'5910974510923776',
        u"page[1][0]['text']": u'You open the email, Luana. \u2028It\u2019s for you!',
        u"page[1][1]['text']": u'Me too!',
        u'skip_editor': [u'1'],
    }

    expected = [
        [TextModuleIndesign(u'baloes_bd_5_1', u'Some time later\u2026'), TextModuleIndesign(u'baloes_bd_6_1', u'Mum, dad! Look, the school email.')],
        [TextModuleIndesign(u'baloes_bd_9_1', u'You open the email, Luana. \u2028It\u2019s for you!'), TextModuleIndesign(u'baloes_bd_8_1', u'Me too!')]
    ]

    assert expected == convert_post_data(data)
