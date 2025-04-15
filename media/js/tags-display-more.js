$(document).ready(function() {
	
	$("div.tags-box").each(function() {
		var lineHeight = $(this).outerHeight();
		var paddingsHeight = lineHeight - $(this).height();
		var divHeight = $(this)[0].scrollHeight;
		if ( lineHeight < divHeight - paddingsHeight ){
			$(this).parent().find("span.more-tags").css("display", "inline-block");
		}
	});
	
	$(document).on("click", ".more-tags", function(){
		var divBox = $(this).parent().find("div.tags-box");
		var link = $(this).find("a");
		if(link.html() == "less"){
			divBox.height("1.1em");
			link.html("more");
		} else {
			divBox.height(divBox[0].scrollHeight);
			link.html("less");
		}
	})
	
});