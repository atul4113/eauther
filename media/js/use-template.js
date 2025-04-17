$(document).ready(function(){
	var button = $("#use-template-button > .button_click");
    var modalWrapper = $(".modal-wrapper");
    var modalContainer = $(".modal-container");
    var html = $("html");
    var closeButton = $(".close-button");
    
    // create modal box
    var shadow = document.createElement("div");
    shadow = $(shadow);
    shadow.addClass("shadow");
    html.append(shadow);
   	shadow.css('z-index', '999').width(html.width()).height(html.height())
   	modalWrapper.css({
	    position:'absolute',
	    left: '50%',
	    top: '50%',
	    marginLeft: "-" + modalWrapper.width()/2 + "px",
	    marginTop: "-" + modalWrapper.height()/2 + "px"
  	}).css('z-index', '1000'); 
   	
   	// create loading gif
   	modalContainer.append("<div class='loading'><img src='/media/images/loading.gif' /></div>");
    $(".loading").css({
	    position:'absolute',
	    left: '50%',
	    top: '50%',
	    marginLeft: "-" + $(".loading").width()/2 + "px",
	    marginTop: "-" + $(".loading").height()/2 + "px"
  	});
    
	button.click(function(){
		// load data
		if( !button.hasClass("loaded") ){
			$.getJSON('/editor/api/templates', function(data) {
				 modalContainer.html('');
				 $.each(data, function(key, val) {
					if(key === "items"){
						$.each(val, function(key, val) {
							modalContainer.append("<div class='single-template'>" +
							"<div class='image'><img src='" + val["icon_url"] + "' /></div>" +
							"<div class='name'>" + val["name"] + "</div>" +
							"<input type='hidden' value='" + val["theme_url"] + "' /></div>");
						})
					}
				 })
			});
		}
		
		button.addClass("loaded");
		
		// open modal box
		modalWrapper.css('display', 'block');
		$(".shadow").css('display', 'block');
	});
    
    
    closeButton.click(function(){
    	modalWrapper.css('display', 'none');
		$(".shadow").css('display', 'none');
    });
    
    $(document).on("click", ".single-template > .image", function(){
    	var templateDiv = $(".templateDiv");
    	var image = $(this).find("img").attr("src");
    	var templateUrl = $(this).parent().find("input").val();
    	
    	templateDiv.find(".image")
    	.html("<img src='" + image + "' />" +
 		"<input type='hidden' name='template_url' value='" + templateUrl + "' />");
    	
   		closeButton.click();
    });
    
});