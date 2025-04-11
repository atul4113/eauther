import sys


FRONTEND_VERSION = '447'
SHARED_SETTINGS = {
    'ealpha-test-application': {
        'app_name': 'eauthor-dev',
        'default_from_email': 'admin@ealpha-test-application.appspotmail.com',
        'server_email': 'admin@ealpha-test-application.appspotmail.com',
        'learnetic_email': 'ealpha619@gmail.com',
        'server_url': 'ealpha-test-application.appspot.com',
        'base_url': 'https://ealpha-test-application.appspot.com',
        'base_secure_url': 'https://ealpha-test-application.appspot.com',
        'user_default_lang': 'en_US',
        'email_subject_prefix': '[Django eAuthor.com]',
        'initial_package_content': 'https://ealpha-test-application.appspot.com/media/icplayer.zip',
        'lesson_default_icon': 'https://ealpha-test-application.appspot.com/media/content/default_presentation.png',
        'secret_key': 'EXAMPLE_SECRET_KEY_TO_CONTACT_OTHER_PLATFORMS',
        'https_redirect': True,
        'rank': 0,
        'home_page': 'https://ealpha-test-application.appspot.com/mauthor/',
        'flexible_account': 'ealpha-test-application@appspot.gserviceaccount.com',
    },
    'mauthor-dev': {
        'app_name': 'mauthor-dev.com',
        'default_from_email': 'mauthor-dev <admin@mauthor.com>',
        'server_email': 'mauthor-dev <admin@mauthor.com>',
        'learnetic_email': 'mauthor@learnetic.com',
        'server_url': 'mauthor-dev.appspot.com',
        'base_url': 'http://www.mauthor-dev.appspot.com',
        'base_secure_url': 'https://mauthor-dev.appspot.com',
        'user_default_lang': 'en_US',
        'email_subject_prefix': '[Django mAuthor-dev.appspot.com]',
        'initial_package_content': 'http://www.mauthor.com/media/icplayer.zip',
        'lesson_default_icon': 'http://www.mauthor.com/media/content/default_presentation.png',
        'secret_key': '',
        'https_redirect': False,
        'rank': 1,
        'home_page': 'http://www.learnetic.com/mauthor/',
        'flexible_account': 'mauthor-dev@appspot.gserviceaccount.com',
    },
    'mauthor-china': {
        'app_name': 'mauthor.cn',
        'default_from_email': 'mauthor.cn@gmail.com',
        'server_email': 'mauthor.cn <mauthor.cn@gmail.com>',
        'learnetic_email': 'mauthor@learnetic.com',
        'server_url': 'mauthor-china.appspot.com',
        'base_url': 'http://www.mauthor.cn',
        'base_secure_url': 'https://mauthor.cn',
        'user_default_lang': 'en_US',
        'email_subject_prefix': '[Django mAuthor.cn]',
        'initial_package_content': 'http://www.mauthor.cn/media/icplayer.zip',
        'lesson_default_icon': 'http://www.mauthor.cn/media/content/default_presentation.png',
        'secret_key': '',
        'https_redirect': False,
        'rank': 2,
        'home_page': 'http://home.mauthor.cn',
        'flexible_account': 'mauthor-china@appspot.gserviceaccount.com',
    }

}


def get_application_names():
    keys = list(SHARED_SETTINGS.keys())
    keys = [k for k in keys if SHARED_SETTINGS[k]['rank'] is not None]

    return sorted(keys, key=lambda k: SHARED_SETTINGS[k]['rank'])

if __name__ == "__main__":
    if sys.argv[1] == 'get_application_names':
        sorted_keys = get_application_names()
        print((','.join(sorted_keys)))
    elif sys.argv[1] == 'get_next_application':
        sorted_keys = get_application_names()
        try:
            key = sys.argv[2]
            if key not in sorted_keys:
                print('')
            else:
                index = sorted_keys.index(key)
                if index + 1 == len(sorted_keys):
                    print('')
                else:
                    print((sorted_keys[index + 1]))
        except IndexError:
            print((sorted_keys[0]))
    elif sys.argv[1] == 'get_next_applications':
        sorted_keys = get_application_names()
        try:
            key = sys.argv[2]
            if key not in sorted_keys:
                print('')
            else:
                index = sorted_keys.index(key)
                if index == len(sorted_keys):
                    print('')
                else:
                    print((','.join(sorted_keys[index:])))
        except IndexError:
            print((','.join(sorted_keys[0:])))
