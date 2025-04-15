$(document).ready(function(){
	$('ul#wiki-pages-list-root-sortable').nestedSortable({
		disableNesting: 'no-nest',
		forcePlaceholderSize: true,
		handle: 'div',
		helper: 'clone',
		items: 'li',
		listType: 'ul',
		opacity: .6,
		placeholder: 'placeholder',
		revert: 250,
		tabSize: 25,
		tolerance: 'pointer',
		toleranceElement: '> div',
		connectWith: 'ul#pages-list-root-sortable'
	}); 
	
	$('ul#pages-list-root-sortable').nestedSortable({
		disableNesting: 'no-nest',
		forcePlaceholderSize: true,
		handle: 'div',
		helper: 'clone',
		items: 'li',
		listType: 'ul',
		opacity: .6,
		placeholder: 'placeholder',
		revert: 250,
		tabSize: 25,
		tolerance: 'pointer',
		toleranceElement: '> div',
		connectWith: 'ul#wiki-pages-list-root-sortable'
	}); 
	
	$('#serialize').on("click", function(){
		var serializedOther = $('ul#pages-list-root-sortable').nestedSortable('serialize');
		$.post("/doc/remove_from_table_of_contents", serializedOther, function(data){
				var serialized = $('ul#wiki-pages-list-root-sortable').nestedSortable('serialize');
				var array = $('ul#wiki-pages-list-root-sortable').nestedSortable('toArray');
				var order = ''
					$.each(array, function(i){
						if($(this)[0]['item_id'] != 'root')
							order += $(this)[0]['item_id']
						if(i + 2 <= array.length && i > 0)
							order += ','
					})
				serialized = serialized + "&order=" + order;
				$.post('/doc/table_of_contents', serialized, function(data) {
					document.location = '/doc';
				});
		});
	});
	
	
});