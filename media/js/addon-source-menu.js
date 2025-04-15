SyntaxHighlighter.all();
	$(document).ready(function(){
		$(".tab-menu").on("click", "div", function(evt){
			$("#" + $(this).attr("sourceId")).slideToggle();
			$(this).toggleClass("selected");
		});
	});