(function(){
    /*
    * Redirect mauthor.com, old.mauthor.com and new.mauthor.com to www.mauthor.com
    * */

    var currentLocation = document.location.href;

    if (currentLocation.indexOf('old.mauthor.com') != -1) {
       currentLocation  = currentLocation.replace('old.mauthor.com', 'mauthor.com');
    }

    if (currentLocation.indexOf('new.mauthor.com') != -1) {
       currentLocation  = currentLocation.replace('new.mauthor.com', 'mauthor.com');
    }

    if (currentLocation.indexOf('www.mauthor.com') == -1 && currentLocation.indexOf('mauthor.com') != -1) {
        currentLocation = currentLocation.replace('mauthor.com', 'www.mauthor.com');
    }

    if (currentLocation != document.location.href) {
        document.location.href = currentLocation;
    }
})();