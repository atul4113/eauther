$(document).ready(function() {
	if (GBrowserIsCompatible()) {
		var map = new GMap2(document.getElementById("gMap"));
		map.setCenter(new GLatLng(54.386156, 18.465203), 15);
		map.setUIToDefault();
		var point = new GLatLng(54.386156, 18.465203);
		map.addOverlay(new GMarker(point));
	}

});