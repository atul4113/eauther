$(document).ready(function(){
	$(".description").each(function(){
		var desc = $(this)
		var more = desc.parent().find("span.more-description")
		var lineHeight = desc.css("line-height").replace('px', '')
		if(desc.height() > lineHeight * 4) {
			desc.css("overflow", "hidden")
			desc.height(lineHeight * 4)
			more.css("display", "block")
		}
	})
	
	$(document).on("click", "span.more-description", function(){
		var divBox = $(this).parent().find(".description")
		var lineHeight = divBox.css("line-height").replace('px', '')
		var link = $(this).find("a");
		if(link.html() == "less"){
			divBox.height(lineHeight * 4);
			link.html("more");
		} else {
			divBox.height(divBox[0].scrollHeight);
			link.html("less");
		}
	})
	
});