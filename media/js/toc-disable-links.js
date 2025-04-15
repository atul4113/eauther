function getPageURL(action) {
	var selected_page = $(".wikiPage");
	var id = selected_page.attr('id');
	if (id) {
		return document.location = '/doc/' + action + '/' + id
	} else {
		alert('There is no page to ' + action + '.')
	}
}

$(document).ready(function(){
	var root = $('#wiki-pages-list-root-not-sortable');
	var rootKids = root.find("li");
	$.each(rootKids, function() {
		var hasRollingList = $(this).has("ul");
		if(hasRollingList.length > 0){
			var rootKid = $(this);
			var image = $(this).children("div").find(".wiki-page-more");
			image.css({
				"background-image" : "url('/media/images/more-arrow.png')",
			    "background-position" : "left",
			    "background-repeat" : "no-repeat"
			});
			image.on("click", function(){
				rootKid.children("ul").toggle();
				$(this).toggleClass("down ");
			});
		}
	});
	
	var selectedLink = root.find(".selected");
	if (selectedLink.length > 0) {
		var parent = selectedLink.parent();
		var selectedLinkList = selectedLink.parent().parent();
		if(selectedLinkList.has("ul").length > 0){
			selectedLinkList.children("ul").toggle();
			parent.children(".wiki-page-more").toggleClass("down ");
		}
		if(root.hasClass("not-sortable")){
			do {
				var div = parent.children("div");
				if( !div.children("a").hasClass("selected") ) {
					parent.children("ul").toggle();
					div.children(".wiki-page-more").toggleClass("down ");
				}
				parent = parent.parent();
			} while( !parent.is(root) );
		}
	}
});
