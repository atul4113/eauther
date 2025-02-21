Osadzenie edytora
===============================================================================


KROK 1. Pierwsza wersja z zapisem i odczytem przygotowanego materiału

* Plik iceditor.zip zawiera przykładowy plik HTML osadzający edytor wraz z przykładowym materiałem.
* Link do materiału podawany jest w pliku HTML komenda: ic_editor.load('files/content.xml');
* Edytor zapisuje zmiany wysyłając POST-a na ten sam URL z którego GET-tem odczytał dane. 
* Strony dodawane są przez portal, więc na razie to nie zadziała
* Logo do edytora powinno być dostepne pod URL-em: /media/short_logo.png

Po zakonczeniu pierwszego kroku powinien być działający edytor, potrafiący edytować zawartość 
przykładowych stron.


KROK 2. Dodawanie nowej prezentacji

* Edytor oczekuje, że pliki XML nowej lekcji będą przygotowane w momencie startu edytora 
  Dlatego portal tworząc nową prezentacją musi stworzyć początkowe pliki składające się z:
  - Pliku contantu
  - Pliku pierwszej strony
* Pliki te są dostępne w katalogu initdata
* Po utworzeniu plików należy w pliku contentu (content.xml) wymienić zmienną {{page.id}} 
  na poprawny URL do pliku strony (page.xml). 


KROK 3. Dodanie nowej strony do prezentacji

* Edytor w celu utworzenia nowej strony wywołuje URL "/editor/api/addNewPage". 
  Wywołanie jest za pomocą komendy POST. W odpowiedzi portal zwraca URL do nowo utworzonej strony


KROK 4. Upload plików

* W celu uploadu pliku na serwer edytor pobiera za pomocą komendy GET na /edito/api/blobUploadDir, 
  URL na który ma być załadowany plik (pozwala to uploadować na serwery zewnętrzne)
* W kolejnym kroku wywołuje upload na podany URL i w odpowiedzi oczekuję URL do wgranego pliku 


KROK 5. Pobieranie modułów zewnętrznych

* Edytor posiada możliwość wczytywania modułów zewnętrznych (addony). 
  Lista dostępnych modułów pobierana jest z url-a: /editor/api/addons. 
  Centralnym repozytorium modułów jest serwis lorepo.com i tam można pobrać listę poprzez url-a:
  http://www.lorepo.com/editor/api/addons
  Tak pobraną listę trzeba dostosować do swoich potrzeb i podać do edytora
* Problem z XSS. Ze względu na zabezpieczenia przeglądarek, edytor nie może samodzielnie wczytywać
  tych addonów z innych serwerów. Dlatego portal musi zapewnić proxy do ich wczytywania. Może to być np.:
  /proxy/get?url=http://www.lorepo.com/public/video/getaddon
  W takiej sytuacji listę addonów podawaną do edytora trzeba odpowiednio zmodyfikować i przygotowac
  na portalu proxy do obsługi requestów.
* Po zakończeniu tego kroku w edytorze w menu modules powinny pojawić się dodatkowe moduły (np. youtube)  
  
  
KROK 6. Szablony  

* Szablon jest zwykła prezentacją
* Edytor pobiera listę szablonów wysyłając GET na /editor/api/templates
* Portal wysyła informację o szablonach jako dokument w formacie json. 
  W dokumencie tym dla każdego szablonu nalezy podać:
  - Nazwę szabonu (dowolny tekst)
  - Link do ikony szablonu
  - Link do pliku contentu
  - Nazwę kategorii (Public)
* Edytor wykorzystuje szablon do wstawiania nowej strony. 
  Aby dodać stronę z szablonu wywoływany jest url /editor/api/addNewPage?page=url_do_strony
* Przykład pliku json z zwracanego przez /editor/api/templates    
{
  	"version": "1",
	"items": [
      	{
      		"name" : "Basic",
      		"icon_url": "http://www.lorepo.com/file/serve/216073", 
      		"theme_url": "/file/430163",
      		"category" : "Public"
      	},
      	{
      		"name" : "Basic",
      		"icon_url": "http://www.lorepo.com/file/serve/216073", 
      		"theme_url": "/file/468051",
      		"category" : "Public"
      	},
    ]
}

Konfiguracja

Edytor jako parametr może otrzymać obiekt z parametrami konfiguracyjnymi. Dozwolone parametry to:
* apiURL - ustawia url do api za pomocą którego edytor komunikuje się z portalem
* showTemplates - (true/false), pozwala określić czy edytor ma pozwalać na wybór szablonów 
* Przykład:
    config = {
    	'apiURL': 'test',
    	'showTemplates' : false,
      	'excludeAddons' : 'Connection, Vimeo'
    }
    ic_editor = icCreateEditor(config);
  
*  excludeAddons - Lista addonów (ich id), które nie mają być pokazywane po uruchomieniu