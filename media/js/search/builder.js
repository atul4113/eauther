
function createContentLogo(content, nextURL) {
	var imageSource = '/media/content/default_presentation.png';
	if(content.content_type == '3') {
		imageSource = '/media/content/default_addon.png';
	}
	if (content.icon_href !== 'None') {
		imageSource = content.icon_href;
	}
	var contentURL = '/' + content.space_type + '/view/' + content.id + '?next=';
	var image = $('<img>').attr('src', imageSource);
	var imageLink = $('<a>').attr('href', contentURL + nextURL);
	imageLink.append(image);
	var logo = $('<div>').append(imageLink);
	return logo;
}

function createContentTitle(content, nextURL) {
	var title = $('<div class="presentation-title">');
	var contentURL = '/' + content.space_type + '/view/' + content.id + '?next=';
	var titleLink = $('<a>').attr('href', contentURL + nextURL);
	titleLink.html(content.title);
	title.append(titleLink);
	return title;
}

function createContentSpace(content) {
	var space = $('<div class="presentation-space">');
	if (content.space_type == 'corporate') {
		content_space_link = 'corporate/list';
		}
	else {
		content_space_link = content.space_type;
	}
	var spaceLink = 'From: <a href="/' + content_space_link + '/' + content.space_id + '">' + content.space_title + '</a>';
	space.append(spaceLink);
	return space
}

function createContentAuthor(content) {
	var author = $('<div class="presentation-author">');
	var authorLink;
	authorLink = '<label>Author: </label>';
	authorLink += '<a href="/public/?author=' + content.author_name + '&type=' + content.content_type + '">';
	authorLink += content.author_name + '</a>';
	author.append(authorLink);
	return author;
}

function createContentEditButton(content, nextURL) {
	var editButton = '<div class="presentation-edit">';
	editButton += '<a href="/mycontent/' + content.id + '/editor?next=' + nextURL + '">Edit</a></div>';
	return editButton;
}

function createContentModifiedDate(content) {
	var modified = '<div class="presentation-modified">';
	modified += 'Modified: ' + content.modified_date + '</div>';
	return modified;
}

function createListElement(content, nextURL, i) {
	
	nextURL = encodeURIComponent(nextURL);
	
	var listElement = $('<li>');
	addFirstOrLastClass(listElement, i);
	
	var logo = createContentLogo(content, nextURL);
	listElement.append(logo);
	
	var title = createContentTitle(content, nextURL);
	listElement.append(title)
	
	var space = createContentSpace(content);
	listElement.append(space);
	
	var author = createContentAuthor(content);
	listElement.append(author);
	
	if (parseInt(content.edit_permission)) {
		var edit = createContentEditButton(content, nextURL);
		listElement.append(edit);
	}
	
	var modified = createContentModifiedDate(content);
	listElement.append(modified);
	
	return listElement;
}

function displayContents(allContents, itemsOnPage, currentPage, isSuperUser) {
	var from = (currentPage - 1) * itemsOnPage;
	var to = currentPage * itemsOnPage;
	allContents = allContents.slice(from, to);
	
	if (allContents.length > 0) {
		var content_ids = '';
		for (var i = 0; i < allContents.length; i++) {
			var content = allContents[i];
			content_ids += content.id;
			if (i<(allContents.length - 1))
				content_ids += ':';
		}
		$('ul.inline-search').html('');
		showLoadingScreen();
		var jqxhr = $.post('/public/get_contents_details', 
				{ 
					'content_ids' :  content_ids
				}).success(function(data) {
					try {
						var result = $.parseJSON(data);
						var allContents = result.contents;
					} catch (e) {
						isError = true;
					}
					
					hideLoadingScreen();
					
					if (isError) {
						displayErrorMessage();
					}
					else {
						for (var i = 0; i < allContents.length; i++) {
							var content = allContents[i];
							
							var listElement = createListElement(content, nextURL, i, isSuperUser);
							
							$('ul.inline-search').append(listElement);
						}
					}
				}).error(function() {
					hideLoadingScreen();
					displayErrorMessage();
				});
	}
	else {
		hideLoadingScreen();
		if (isError) {
			displayErrorMessage();
		}
	}
}

function createErrorMessage(message) {
	var errorContainer = $('<div>').css({
							'color' : '#D8000C',
							'float' : 'left'
						});
	errorContainer.append(message);
	return errorContainer;
}