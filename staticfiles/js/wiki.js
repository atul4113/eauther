function setWikiPage(){
		if(typeof(Storage)=="undefined"){
			alert('Local storage not implemented')
		}
		else{
			var text = $('#id_text').val();
			if (!text) {text=" ";}
			var title = $('#id_title').val();
			if (!title) {title=" ";}
			localStorage.setItem('pageText', text);
			localStorage.setItem('pageTitle', title);
		}
	}
	
function getWikiPage(){
		if(localStorage.pageText){
			$('#id_text').val(localStorage.getItem('pageText'));
		}
		if(localStorage.pageTitle){
			$('#id_title').val(localStorage.getItem('pageTitle'));
		}
	}