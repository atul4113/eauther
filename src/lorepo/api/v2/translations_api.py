import json
import zlib

from django.conf.urls import url

import settings
from libraries.utility.environment import get_versioned_module
from libraries.utility.helpers import get_object_or_none
from libraries.utility.queues import trigger_backend_task
from lorepo.api.v2.util import RetrieveOrListAPIView, CreateUpdateDestroyAPIView
from lorepo.translations.images import images_labels
from lorepo.translations.models import SupportedLanguages, TranslatedLang, ImportTable, TranslatedImages
from lorepo.translations.serializers import LanguagesSerializer, ImportSerializer, AddLabelSerializer, \
    EditLabelSerializer, ImageSerializer
from lorepo.translations.utils import get_translated_images
from rest_framework import views, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404, DestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


class TranslationsView(views.APIView):

    """
    @api {get} /api/v2/translations/ /translations/
    @apiDescription Returns translations dictionary for specified language.
    If lang_id isn't specified, the dictionary is returned for default instance language
    @apiName Translations
    @apiGroup Translations

    @apiSuccessExample {json} Success-Response:
     HTTP/1.1 200 OK
       {
          "labels":{
             "ecommerce.Type_something_to_find_course":"Type something to find course"
          },
          "images":{
             "mcourser_logo_shadow.svg":"/file/serve/6343125530312704",
             "home_description_mcourser_logo":"/file/serve/6404423303561216",
             "mcourser_logo_header":"/file/serve/6263685815205888",
             "mcourser_logo_drawer":"/file/serve/6545160791916544",
             "free.png":"/file/serve/6472996751409152"
          }
       }
    """

    permission_classes = (AllowAny,)

    def get(self, request, lang_id, *args, **kwargs):

        if lang_id:
            params = {
                'pk': lang_id
            }
        else:
            params = {
                'lang_key': settings.USER_DEFAULT_LANG
            }

        lang = get_object_or_none(SupportedLanguages, **params)

        if lang is None:
            return Response({
                "labels": {},
                "images": {}
            })

        params['lang_key'] = lang.lang_key

        trans_lang = TranslatedLang.get_or_none(params['lang_key'])
        if trans_lang is None:
            trans = {}
        else:
            trans = trans_lang.translations

        response = {
            "labels": trans,
            "images": get_translated_images(lang),
        }
        return Response(response)


class LanguagesView(CreateAPIView, UpdateAPIView, RetrieveOrListAPIView, DestroyAPIView, views.APIView):

    """
        @api {post} /api/v2/translations/languages /translations/languages
        @apiDescription adding new language
        @apiName LanguageAdd
        @apiGroup Translations
        @apiPermission Staff
        @apiParam {String} [lang_key] example en_US
        @apiParam {String} [lang_description] language description
        @apiParamExample {json} Request-Example:
            {
              "lang_key": "en_US",
              "lang_description": "english"
            }

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 201 OK
          {
            "created_date": "2017-07-27T02:40:26.204017",
            "id": 5724160613416960,
            "lang_description": "english do usuniecia",
            "lang_key": "en_US7",
            "modified_date": "2017-07-27T02:40:26.204049"
          }

    """

    """
        @api {get} /api/v2/translations/languages /translations/languages
        @apiDescription get all supported languages
        @apiName LanguagesList
        @apiGroup Translations
        @apiPermission Staff
    
        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }
    
        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
            [
                {
                    "created_date": "2017-07-26T08:15:52.472832", 
                    "id": 4987281664376832, 
                    "lang_description": "english do usuniecia", 
                    "lang_key": "en_US6", 
                    "modified_date": "2017-07-26T08:15:52.472876"
                }, 
                {
                    "created_date": "2017-07-20T08:14:32.067351", 
                    "id": 5252951161438208, 
                    "lang_description": "partial update", 
                    "lang_key": "en_US", 
                    "modified_date": "2017-07-26T08:15:05.171969"
                }
            ]
    """
    """
        @api {put} /api/v2/translations/languages/<lang_id> /translations/languages/<lang_id>
        @apiDescription Edit language
        @apiName EditLanguage
        @apiGroup Translations
        @apiPermission Staff
        @apiParam {String} [lang_key] en_US
        @apiParam {String} [lang_description] lang description
        @apiParamExample {json} Request-Example:
            {
               "lang_key": "en_US",
               "lang_description": 'language description'
            }
    
        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }
    
        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK

    """
    """
       @api {delete} /api/v2/translations/languages/<lang_id> /translations/languages/<lang_id>
       @apiDescription Remove language by lang_id
       @apiName RemoveLanguage
       @apiGroup Translations
       @apiPermission Staff
       @apiParam {String} [label] label name
    
    
       @apiHeader {String} Authorization User Token.
       @apiHeaderExample {json} Header-Example:
         {
           "Authorization": "JWT TOKEN"
         }
    
       @apiSuccessExample {json} Success-Response:
         HTTP/1.1 204 No Content
    """

    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = LanguagesSerializer
    queryset = SupportedLanguages.objects.all()
    lookup_url_kwarg = 'lang_id'

    def partial_update(self, request, *args, **kwargs):
        if 'lang_key' in self.request.data:
            tl = get_object_or_404(TranslatedLang, lang_id=kwargs.get('lang_id'))
            tl.lang_key = self.request.data['lang_key']
            tl.save()
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        lang = serializer.save()

        url = '/translations/add_language_async/%s/%s' % (lang.id, self.request.user.id)
        trigger_backend_task(url, target=get_versioned_module('localization'))

    def perform_destroy(self, instance):
        url = '/translations/delete_lang_async/%s/%s' % (instance.pk, self.request.user.id)
        trigger_backend_task(url, target=get_versioned_module('localization'))


class ImportView(CreateAPIView, views.APIView):

    """
    @api {post} /api/v2/translations/import /translations/import
    @apiDescription Importing translations labels 
    @apiName ImportLabels
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {Number} [lang] example en_US
    @apiParam {String} [import_json] json with translations labels
    @apiParam {Boolean} [create_notification] should send notification
    @apiParamExample {json} Request-Example:
        {
          "lang": 12131312,
          "create_notification": True,
          "import_json": {"label1": "value"}
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Lang not exists",
        "code":"0"
    }

    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = ImportSerializer

    def post(self, request, *args, **kwargs):
        import_serializer = self.get_serializer(data=self.request.data)
        import_serializer.is_valid(raise_exception=True)
        validated_data = import_serializer.validated_data

        try:
            lang = SupportedLanguages.objects.get(pk=validated_data.get('lang'))
        except SupportedLanguages.DoesNotExist:

            raise ValidationError({'message': 'Lang not exists', 'code': 0})

        my_import = ImportTable(lang=lang, user=self.request.user,
                                pasted_json=json.dumps(validated_data.get('pasted_json')))
        if validated_data.get('create_notification', False):
            my_import.create_notification = True

        my_import.save()

        url = '/translations/import/2/%s' % (my_import.id)
        trigger_backend_task(url, target=get_versioned_module('localization'))

        return Response({}, status=status.HTTP_201_CREATED)


class ResolveConflictsView(views.APIView):

    """
    @api {post} /api/v2/translations/import/resolve_conflicts/<id> /translations/import/resolve_conflicts/<id>
    @apiDescription Resolving conflicts after import translations labels
    @apiName ResolvingConflicts
    @apiGroup Translations
    @apiParam {Number} [import_table_id] id from email
    @apiParam {String} [replace_conflict] json with labels structure for more see request example
    @apiPermission Staff
    @apiParamExample {json} Request-Example:
        {"replace_conflict": 
            {
            "1": {"lang_key": "en_US", "name": "upload_icon.Upload", "value": "Upload121"}, 
            "3": {"lang_key": "en_US", "checked": "3", "name": "upload_icon.Current_icon", "value": "Current icon1121:"}, 
            "2": {"lang_key": "en_US", "checked": "2", "name": "upload_icon.No", "value": "No1121"}
            }
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    """
    """
    @api {get} /api/v2/translations/import/resolve_conflicts/<id> /translations/import/resolve_conflicts/<id>
    @apiDescription get log 
    @apiName LanguagesList
    @apiGroup Translations
    @apiPermission Staff

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            {
                "created_date": "2017-07-26T08:15:52.472832", 
                "id": 4987281664376832, 
                "lang_description": "english do usuniecia", 
                "lang_key": "en_US6", 
                "modified_date": "2017-07-26T08:15:52.472876"
            }, 
            {
                "created_date": "2017-07-20T08:14:32.067351", 
                "id": 5252951161438208, 
                "lang_description": "partial update", 
                "lang_key": "en_US", 
                "modified_date": "2017-07-26T08:15:05.171969"
            }
        ]
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "replace_conflict not provideded",
        "code":"0"
    }
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, id, *args, **kwargs):
        my_import = get_object_or_404(ImportTable, pk=id)
        replace_conflict = self.request.data.get('replace_conflict')
        if replace_conflict is None:
            raise ValidationError({'message': 'replace_conflict not provideded', 'code': 0})

        my_import.deflated_conflict_rep = zlib.compress(json.dumps(replace_conflict))
        my_import.save()
        url = '/translations/import/4/%s' % (id)
        trigger_backend_task(url, target=get_versioned_module('translations'), queue_name='localization')

        return Response({})

    def get(self, request, id, *args, **kwargs):
        my_import = get_object_or_404(ImportTable, pk=id)
        log = {
            'added': json.loads(my_import.added),
            'conflict': json.loads(zlib.decompress(my_import.deflated_conflict)),
            'omitted': json.loads(my_import.omitted),
            'not_valid': json.loads(my_import.not_valid)
        }

        return Response(log)


class LabelView(CreateAPIView, views.APIView):

    """
    @api {post} /api/v2/translations/label /translations/label
    @apiDescription Adding label to all languages
    @apiName AddLabel
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {Number} [lang_id] example 12131312
    @apiParam {String} [import_json] json with labels
    @apiParam {Boolean} [create_notification] should send notifications to editors
    @apiParamExample {json} Request-Example:
        {
          "lang_id": 12131312,
          "create_notification": True,
          "import_json": {"label1": "value"}
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation language not exist",
        "code":"3"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation label already exists",
        "code":"2"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation malformed",
        "code": 1,
        "additional_message": "additional information"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation conflict for key %s. You have to edit this label." % key,
        "code": 0
    }
    """

    """
    @api {put} /api/v2/translations/label /translations/label
    @apiDescription Edit label to specific language
    @apiName EditLabel
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {String} [lang_key] en_US
    @apiParam {String} [name] label
    @apiParam {String} [value] label value
    @apiParamExample {json} Request-Example:
        {
          "lang_key": "en_US",
          "name": "label1",
          "value": "value"
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation language not exist",
        "code":"3"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation label already exists",
        "code":"2"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation malformed",
        "code": 1,
        "additional_message": "additional information"
    }
    @apiErrorExample {json} Error-Response:
    HTTP/1.1 400 Bad Request
    {
        "message": "Translation conflict for key %s. You have to edit this label." % key,
        "code": 0
    }

    """

    """
    @api {delete} /api/v2/translations/label /translations/label
    @apiDescription Remove label from all languages
    @apiName RemoveLabel
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {String} [label] label name
    
    
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
     {
       "Authorization": "JWT TOKEN"
     }
    
    @apiSuccessExample {json} Success-Response:
     HTTP/1.1 204 No Content

   """

    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = AddLabelSerializer

    def post(self, request, *args, **kwargs):
        import_serializer = self.get_serializer(data=self.request.data)
        import_serializer.is_valid(raise_exception=True)
        validated_data = import_serializer.validated_data

        languages = SupportedLanguages.objects.all()
        for lang in languages:
            label = {
                'name': validated_data.get('name'),
                'lang': lang.lang_key,
                'value': validated_data.get('value')
            }
            TranslatedLang.add_translation(label)

        return Response({}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        for tl in TranslatedLang.objects.all():
            try:
                tl.delete_translation(key=kwargs.get('label'))
                tl.save()
            except KeyError:
                pass
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        edit_serializer = EditLabelSerializer(data=self.request.data)
        edit_serializer.is_valid(raise_exception=True)
        validated_data = edit_serializer.validated_data
        label = {
            'name': validated_data.get('name'),
            'lang': validated_data.get('lang_key'),
            'value': validated_data.get('value')
        }

        TranslatedLang.add_translation(label, overwrite=True)

        return Response({}, status=status.HTTP_200_OK)


class ImageView(CreateUpdateDestroyAPIView, RetrieveOrListAPIView):

    """
    @api {post} /api/v2/translations/image /translations/image
    @apiDescription Adding Image to language
    @apiName AddImage
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {Number} [file] example 12131312
    @apiParam {Number} [lang] example 12131312
    @apiParam {String} [label] label from defined list in images.py
    @apiParamExample {json} Request-Example:
        {
          "file": 4566306149892096,
          "lang": 5252951161438208,
          "label": "mauthor_logo_shadow.svg"
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 201 OK 
        {
            "created_date": "2017-07-27T05:25:05.676181", 
            "file": 4566306149892096, 
            "id": 4738998194929664, 
            "label": "mauthor_logo_shadow.svg", 
            "lang": 5252951161438208, 
            "modified_date": "2017-07-27T05:25:05.676297"
        }
    """

    """
    @api {put} /api/v2/translations/image/<pk> /translations/image/<pk>
    @apiDescription Edit Image to language
    @apiName EditImage
    @apiGroup Translations
    @apiPermission Staff
    @apiParam {Number} [file]  12131312
    @apiParam {Number} [lang]  12131312
    @apiParam {String} [label] label from defined list in images.py
    @apiParamExample {json} Request-Example:
        {
          "file": 4566306149892096,
          "lang": 5252951161438208,
          "label": "mauthor_logo_shadow.svg"
        }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 201 OK 
        {
            "created_date": "2017-07-27T05:25:05.676181", 
            "file": 4566306149892096, 
            "id": 4738998194929664, 
            "label": "mauthor_logo_shadow.svg", 
            "lang": 5252951161438208, 
            "modified_date": "2017-07-27T05:25:05.676297"
        }
    """
    """
    @api {delete} /api/v2/translations/image/<id> /translations/image/<id>
    @apiDescription Delete Image
    @apiName EditImage
    @apiGroup Translations
    @apiPermission Staff
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 204 NO Content 

    """

    """
    @api {get} /api/v2/translations/image /translations/image
    @apiDescription Get Images from all languages
    @apiName GetImages
    @apiGroup Translations
    @apiPermission Staff
    
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK 
        [
            {
                "created_date": "2017-07-27T05:55:36.888779", 
                "file": 4566306149892096, 
                "id": 5301948148350976, 
                "label": "mauthor_logo_shadow.svg", 
                "lang": 5252951161438208, 
                "modified_date": "2017-07-27T05:55:36.888818"
            }
        ]
    """

    """
    @api {get} /api/v2/translations/image/<id> /translations/image/<id>
    @apiDescription Get Image by id
    @apiName GetImages
    @apiGroup Translations
    @apiPermission Staff

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK 
        {
            "created_date": "2017-07-27T05:55:36.888779", 
            "file": 4566306149892096, 
            "id": 5301948148350976, 
            "label": "mauthor_logo_shadow.svg", 
            "lang": 5252951161438208, 
            "modified_date": "2017-07-27T05:55:36.888818"
        }
    """
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = ImageSerializer
    lookup_url_kwarg = 'id'
    queryset = TranslatedImages.objects.all()


class ImageLabels(views.APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    """
    @api {get} /api/v2/image/labels /image/labels
    @apiDescription Get Images labels
    @apiName GetImagesLabels
    @apiGroup Translations
    @apiPermission Staff

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            [
                "mauthor_logo_shadow.svg",
                "Logo in header"
            ],
            [
                "mauthor_footer_logo.svg",
                "Logo in footer"
            ]
        ]
    """
    def get(self, request):
        return Response(images_labels)

urlpatterns = [
    url(r'^(?P<lang_id>\d+){0,1}$', TranslationsView.as_view(), name='translations'),
    url(r'^languages(/(?P<lang_id>\d+))?$', LanguagesView.as_view(), name='languages'),
    url(r'^import/resolve_conflicts/(?P<id>\d+)$', ResolveConflictsView.as_view(), name='resolve'),
    url(r'^import$', ImportView.as_view(), name='import'),
    url(r'^label(/(?P<label>[\w\/\.\-]+))?$', LabelView.as_view(), name='label'),
    url(r'^image(/(?P<id>\d+))?$', ImageView.as_view(), name='image'),
    url(r'^image/labels$', ImageLabels.as_view(), name='image'),
]
