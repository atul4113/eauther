(function($) {
	// Source: http://stackoverflow.com/questions/2655925/how-to-apply-important-using-css/8894528#8894528
	if ($.fn.style) {
		return;
	}

	// Escape regex chars with \
	var escape = function(text) {
		return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
	};

	// The style function
	$.fn.style = function(styleName, value, priority) {
		// DOM node
		var node = this.get(0);
		// Ensure we have a DOM node
		if (typeof node == 'undefined') {
			return this;
		}
		// CSSStyleDeclaration
		var style = this.get(0).style;
		// Getter/Setter
		if (typeof styleName != 'undefined') {
			if (typeof value != 'undefined') {
				// Set style property
				priority = typeof priority != 'undefined' ? priority : '';
				style.setProperty(styleName, value, priority);
				return this;
			} else {
				// Get style property
				return style.getPropertyValue(styleName);
			}
		} else {
			// Get CSSStyleDeclaration
			return style;
		}
	};
})(jQuery);

var draggingOptions,
	resizingOptions,
	isSnappingMode = false,
	snapItems = [],
	gridEyeSize;

function makeString(modules, grid, rulers) {
	var str = "";
	
	if(modules !== undefined) str+=snapItems[0]+",";
	if(grid !== undefined) str+=snapItems[1]+",";
	if(rulers !== undefined) str+=snapItems[2];
	
	return str;
}

var keyModule = null, keySelector = null, initializedEvent = false;
var modules = [];
var ids;
var	startModulesPositionsKeyPress = [],
	uiPositionStart = {},
	selectors = [];

var lastFire = new Date();

var utilityObject = {
    // Set a flag if SelectionController should capture events from Content.
    // It's recommended to set to false when some events occurence, e.g. dragging elements over Content
    captureEvents: function(capture) {
        if (shouldSelectorControllerCaptureEvents) {
            shouldSelectorControllerCaptureEvents(capture);
        }
    }
};
var wasModuleAddedByDrag = false;
//In this function implement methods that must be called after all editor content is initialized.
window.iceOnEditorInitialized = function () {
	var uiPositionTop, uiPositionLeft;
	var draggedModuleId = null;
	var firstLaunch = true;
	
	function onStartDraggedModule(event, ui, that) {
		$(ui.helper).css({'position': 'absolute', 'z-index':'9000'});
		wasModuleAddedByDrag = true;
		utilityObject.captureEvents(false);
	}
	
	function onStopDraggedModule(event, ui, that, isFavourite) {
		if($(".ic_header.ic_page:visible").length > 0){
			uiPositionTop = $(ui.helper).position().top - $("#ruler_horizontal").height() - $(".ic_header.ic_page").height() + $("#content").scrollTop()-1;
		}else{
			uiPositionTop = $(ui.helper).position().top - $("#ruler_horizontal").height() + $("#content").scrollTop()-1;
		}

		uiPositionLeft = $(ui.helper).position().left - $("#ruler_vertical").width()-1;
		
		if(isFavourite){
			uiPositionTop += 3;
			uiPositionLeft += 4;
		}
		
        var coords = $('.ic_page.ic_main').position();
        coords.bottom = coords.top + $('.ic_page.ic_main').height();
        coords.bottomRight = coords.left + $('.ic_page.ic_main').width();
        if(ui.position.top >= coords.top && ui.position.top <= coords.bottom && ui.position.left >= coords.left && ui.position.left <= coords.bottomRight){
        	$(that).click();
        	if(!isFavourite){
        		$("#addModulePage").css("display", "block");
        	}
        }else{  
        }
        utilityObject.captureEvents(true);
	}
	
	function addDraggableToFavouriteModule() {
		var favouriteModules = $(".favouritiesMenuPanel").find(".additionalItem:not(#favouriteModulesButton)");
		
		favouriteModules.draggable({
			appendTo: "#contentWrapper",
			helper: "clone",
			distance: 10,
			start: function(event, ui) {
				onStartDraggedModule(event, ui, this);
			},
			stop: function(event, ui) {
				onStopDraggedModule(event, ui, this, true);
			}
		});
		
		$(".ice_module_icon").draggable({
			appendTo: "#contentWrapper",
			helper: "clone",
			distance: 10,
			start: function(event, ui) {
				onStartDraggedModule(event, ui, this);
			},
			stop: function(event, ui) {
				onStopDraggedModule(event, ui, this, false);
			}
		});
	}
	
	window.addDraggableToFavouriteModule = function() {
		addDraggableToFavouriteModule();
	};
	
	addDraggableToFavouriteModule();
	
	window.isAddToDragAction = function () {
		return wasModuleAddedByDrag;
	};
	
	window.onAddToDragAction = function () {
        var $moduleSelector = $('.moduleSelector.selected');
        var $module;
        
        if(!wasModuleAddedByDrag){
        	$module = $moduleSelector.prev();
            draggedModuleId = $module.attr("id");
        }
        
        if ($moduleSelector.length != 0 && $moduleSelector.prev().attr("id") != draggedModuleId && wasModuleAddedByDrag){
            $module = $moduleSelector.prev();
            draggedModuleId = $module.attr("id");
            
	        $module.css({
            	top: uiPositionTop + 'px',
            	left: uiPositionLeft + 'px'
            });
        	$moduleSelector = $module.next();
        	
        	$moduleSelector.css({
            	top: uiPositionTop + 'px',
            	left: uiPositionLeft + 'px'
        	});

        	iceModulePositionChanged($module.attr("id"), uiPositionLeft, uiPositionTop, null, null, true, false);
        	wasModuleAddedByDrag = false;
        }
	};
	
	// Resizing columns
	$( "#leftResizer" ).draggable({
		containment: "#leftResizerContainment",
		axis: "x",
		scroll: false,
		iframeFix: true,
		start: function(event, ui) {
            utilityObject.captureEvents(false);
		},
		drag: function(event, ui) {
			$('#leftCol').css("width",ui.position.left+9);
			$('#contentWrapper').css("left",ui.position.left+9);
		},
		stop: function () {
			window.iceUpdateScrollbars();
			window.iceUpdatePageResizers();

            utilityObject.captureEvents(true);

        }
	});	
	
	var $rightCol = $('#rightCol'),
		$rightResizer = $("#rightResizer"),
		windowWidth;
	
	$rightResizer.draggable({
		containment: "#rightResizerContainment",
		iframeFix: true,
		axis: "x",
		scroll: false,
		start: function(event, ui) {
            utilityObject.captureEvents(false);
            windowWidth = $(window).width();
		},
		drag: function(event, ui) {
			// 9 pixels comes from rightResizer width (CSS styles)
			ui.position.left = Math.min( windowWidth - 209, ui.position.left );
			
			$rightCol.css("width",$('#editorContainer').width() - ui.position.left - 9);
			$('#contentWrapper').css("right", $rightCol.width() + 9);
		},
		stop: function(event, ui) {
			$rightResizer.css("left", "auto");
			$rightResizer.css("right", $rightCol.width());
			
			window.iceUpdatePageResizers();
			window.iceUpdateScrollbars();
            utilityObject.captureEvents(true);
        }
	});

	if(firstLaunch) {
        $('#contentWrapper').css("right", 300 + 9);
        $rightCol.css("width", 300);
        $rightResizer.css("left", "auto");
        $rightResizer.css("right", 300);
	    firstLaunch = false;
    }

	var $mainPage = $('#contentWrapper').find('.mainPage').not("#previewPage"),
		$rightWindowResizer = '<div class="rightWindowResizer"></div>';

	$mainPage.prepend($rightWindowResizer);
	$mainPage.resizable({
		handles: 'w',
		iframeFix: true,
		start: function() {
            utilityObject.captureEvents(false);

            // iframeFix
		    $('<div class="ui-resizable-iframeFix" style="background: #fff;"></div>').css({
                width:'100%', 
                height: '100%',
                position: "absolute", 
                opacity: "0.001", 
                zIndex: 1000
            }).appendTo("body");
		},
		stop: function() {
			$('.ui-resizable-iframeFix').remove();

            utilityObject.captureEvents(true);

            $(this).css("height" , "");
            window.postMessage("RESIZE_EDITOR","*");
		}
	});
	
	var pagePosition = {left: 0, top: 0},
		pageWidth = 0, pageHeight = 0, footerHeight = 0,
		$page, $presentation;
	
	// IDs of resizers are determined by their appearances but they resize page
	// in direction suggested by variable names.
	var $pageResizerHorizontal = $("#presentationResizer-vertical"),
		$pageResizerVertical = $("#presentationResizer-horizontal"),
		$pageInfo = $('<div id="moduleInfo"></div>');
	
	function sendPageSelectedInfo() {
		window.selectedModuleID = null;
		
		if (icePageSelected !== undefined) {
			icePageSelected();
		}
	}
	
	function updatePageInfoBox(event, width, height) {
		var roundedWidth = parseInt(width, 10);
		var roundedHeight = parseInt(height, 10);
		
		$pageInfo.html(roundedWidth + "px, " + roundedHeight + "px");
		$pageInfo.css({top: event.pageY + 2, left: event.pageX + 20});
	}
	
	function getFooterHeight() {
		var $footerLock = $('#footerLock');

		// Footer Lock will be invisible if footer is not displayed (f.e. when it's edited as normal page).
		return $footerLock.is(":visible") ? $footerLock.height() : 0;
	}
	
	$pageResizerHorizontal.draggable({
		axis: "x",
		scroll: false,
		iframeFix: true,
		start: function(event, ui) {
			$page = $('.ic_page.ic_main');
			$presentation = $('#presentation');
			pagePosition = $page.position();
			pageWidth = $page.width();
			pageHeight = $page.height();

            utilityObject.captureEvents(false);

            sendPageSelectedInfo();
			
			updatePageInfoBox(event, pageWidth, pageHeight);
            $("#editorContainer").append($pageInfo);
		},
		drag: function(event, ui) {
			pageWidth = ui.position.left - pagePosition.left;

			$page.width(pageWidth);
			$presentation.width(pageWidth);
			
			var roundedPageWidth = parseInt(pageWidth, 10);
			var roundedPageHeight = parseInt(pageHeight, 10);
			
			icePageDimensionsChanged(roundedPageWidth, roundedPageHeight, false);
			updatePageInfoBox(event, roundedPageWidth, roundedPageHeight);
		},
		stop: function (event, ui) {
			pageWidth = ui.position.left - pagePosition.left;
			if (pageWidth != $page.width()) {
				// When presentation styles overrides inline dimensions from dragging
				// we need to restore those dimensions.
				pageWidth = $page.width();
			}

			$page.width(pageWidth);
			$presentation.width(pageWidth);
			
			icePageDimensionsChanged(pageWidth, pageHeight, true);

            utilityObject.captureEvents(true);

			$pageInfo.remove();
		}
	});
	
	$pageResizerVertical.draggable({
		axis: "y",
		scroll: false,
		iframeFix: true,
		start: function(event, ui) {
			$page = $('.ic_page.ic_main');
			$presentation = $('#presentation');
			pagePosition = $page.position();
			pageWidth = $page.width();
			pageHeight = $page.height();
			footerHeight = getFooterHeight();

            utilityObject.captureEvents(false);

			sendPageSelectedInfo();
			$("#editorContainer").append($pageInfo);
			updatePageInfoBox(event, pageWidth, pageHeight);
		},
		drag: function(event, ui) {
			pageHeight = ui.position.top - pagePosition.top - footerHeight;

			$page.height(pageHeight);
			$presentation.height(pageHeight + pagePosition.top + footerHeight);
			
			var roundedPageWidth = parseInt(pageWidth, 10);
			var roundedPageHeight = parseInt(pageHeight, 10);
			icePageDimensionsChanged(roundedPageWidth, roundedPageHeight, false);
			updatePageInfoBox(event, roundedPageWidth, roundedPageHeight);
		},
		stop: function (event, ui) {
			pageHeight = ui.position.top - pagePosition.top - footerHeight;
			
			if (pageHeight != $page.height()) {
				// When presentation styles overrides inline dimensions from dragging
				// we need to restore those dimensions.
				pageHeight = $page.height();
			}

			$page.height(pageHeight);
			$presentation.height(pageHeight + pagePosition.top + footerHeight);
			
			icePageDimensionsChanged(pageWidth, pageHeight, true);

            utilityObject.captureEvents(true);

			$pageInfo.remove();
		}
	});
	
	window.iceUpdatePageResizers = function() {
		var $page = $('.ic_page.ic_main'),
			pageOffset = $page.offset(),
			containment = [pageOffset.left + 1, pageOffset.top + getFooterHeight() + 1,
			               Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER];
		
		$pageResizerHorizontal.draggable( "option", "containment", containment);
		$pageResizerVertical.draggable( "option", "containment", containment);
		
		$pageResizerHorizontal.css('left', '100%');
		$pageResizerVertical.css('top', '100%');
	};
	
	iceUpdatePageResizers();
	
	// Main menu
	function handleHoverMenu($menuItems, reduceSize) {
		var isMenuHidden = false;
		$menuItems.mouseenter(function(){
			function reduceSubMenuHeight() {
				var offsetTop = $subMenu.offset().top,
				windowHeight = $(window).height(),
				availableHeight = windowHeight - offsetTop;
				
				if (availableHeight < $subMenu.height()) {
					$subMenu.height(availableHeight);
				}
			}
			
			var $subMenu = $(this).find('> ul');
			
			if (reduceSize && $subMenu.offset() != null) {
				reduceSubMenuHeight();
				Ps.initialize($subMenu[0]);
			}

			/**
			 * jQuery UI resizable closes menu (semi-triggers mouseleave event) on every element
			 * that is on top of the one that should be resized. Module selectors are those elements and
			 * we need to disable all resizing when sub menus are showed.
			 */
			disableModuleSelectors($('.ic_page.ic_main .moduleSelector-resizable'));
			$subMenu.show();
			isMenuHidden = false;
		});
		
		$menuItems.mouseleave(function(){
			enableModuleSelectors($('.ic_page.ic_main .moduleSelector-resizable'));
			$(this).find('> ul').hide();
			if(reduceSize){
				isMenuHidden = true;
			}else{
				isMenuHidden = false;
			}
		});
		
		$menuItems.find('a').click(function () {
			if(!isMenuHidden){
				$menuItems.find('> ul').hide();
				isMenuHidden = true;
			}else{
				$(this).next().show();
				isMenuHidden = false;
			}
		});
	}
	
	handleHoverMenu($("ul.level0 li"), false);
	handleHoverMenu($("ul.level1 li"), true);
	
	window.disableModuleSelectors = function ($modules) {
		$modules.resizable('disable');
	};
	
	window.enableModuleSelectors = function ($modules) {
		$modules.resizable('enable');
	};

	// Scrollbars
	var $scrollableBoxes = $('#modulesList, #pagesList-navigation, #pagesList-commons, #content, .propertiesItemsListWrapper, .propertiesStaticItemsListWrapper, #propertiesList, .contents.scrollable');
	$scrollableBoxes.each(function (_, element) {
		Ps.initialize(element);
	});
	
	window.iceAddScrollBar = function(selector) {
		Ps.initialize($(selector)[0]);
	};
	
	window.iceUpdateWidgetScrollbars = function(widgetElement) {
		// all scroolbars excluded PagesWidget should be refreshed
		if (widgetElement === "pages") {
			$scrollableBoxes.each(function (_, element) {
				if (element.getAttribute('id') != 'pagesList-navigation' && element.getAttribute('id') != 'pagesList-commons') {
					element.scrollTop = 0;
				}

				Ps.update(element);
			});
		} else {
			if (widgetElement === "properties") {
				$element = $('#propertiesList')[0];
			} else if (widgetElement === "modules") {
				$element = $('#modulesList')[0];
			} else if (widgetElement === "content") {
				$element = $('#content')[0];
			} else if (widgetElement === "gapItemsList") {
				$element = $('.gapItemsList')[0];
			}
			
			if ($element) return;
			
			$element.scrollTop = 0;
			Ps.update($element);
		}
	};
	
	window.iceUpdateScrollbars = function () {
		$scrollableBoxes.each(function (_, element) {
			if (element.getAttribute('id') != 'content') {
				element.scrollTop = 0;
			}

			Ps.update(element);
		});
	};

	//RULERS
	var rulers = {
			verticals: [],
			horizontals: [],
			
			update: function() {
				this.verticals.length = 0;
				this.horizontals.length = 0;
				
				var that = this,
					$verticalRuler = $("#presentation").find(".ruler-wrapper.vertical"),
					$horizontalRuler = $("#presentation").find(".ruler-wrapper.horizontal");
				
				$.each($verticalRuler, function(_, ruler) {
					that.verticals.push($(ruler).position().left);
				});
				
				$.each($horizontalRuler, function(_, ruler) {
					if ($(ruler).position().top === 0 || $(ruler).position().top === pageTop) {
						$(ruler).addClass("initial");
						$(ruler).css("top", pageTop + "px");
					} else {
						$(ruler).removeClass("initial");
					}
					
					if(!$(ruler).hasClass("initial")){
						that.horizontals.push($(ruler).position().top);
					}
				});
				
				iceUpdateRulersPositions(that.verticals, that.horizontals);
				this.connectHandlers();
			},
			
			connectHandlers: function() {
				var $rulerWrapper = $("#presentation").find(".ruler-wrapper");
				
				$rulerWrapper.mousedown(function() {
                    utilityObject.captureEvents(false);
				});
				
				$rulerWrapper.mouseup(function() {
                    utilityObject.captureEvents(true);
                });
			},
			
			removeVertical: function($ruler, position) {
				$ruler.remove();
				
				var index = this.verticals.indexOf(position);

				if (index > -1) {
					this.verticals.splice(index, 1);
				}
			},
			
			removeHorizontal: function($ruler, position) {
				if (!$ruler.hasClass("initial")) {
					$ruler.remove();
					
					var index = this.horizontals.indexOf(position);
					if (index > -1) {
						this.horizontals.splice(index, 1);
					}
				}
			},

			canAddNewVertical: function() {
				return this.verticals.length < 40;
			},
			
			canAddNewHorizontal: function() {
				return this.horizontals.length < 40;
			},
			
			getVerticalLength: function() {
				return this.verticals.length;
			},
			
			getHorizontalLength: function() {
				return this.horizontals.length;
			},
			
			canRemoveVertical: function() {
				return this.verticals.indexOf(0) !== -1;
			},
			
			canRemoveHorizontal: function() {
				return this.horizontals.indexOf(0) !== -1;
			},
			
			isNoRulers: function() {
				return this.horizontals.length === 0 && this.verticals.length === 0;
			},
			
			clear: function() {
				$horizontalRulers = $(".ruler-wrapper.horizontal");
				$verticalRulers = $(".ruler-wrapper.vertical");
				
				$horizontalRulers.off();
				$verticalRulers.off();
				
				$.each($horizontalRulers, function(_, el) {
					$(el).remove();
				});

				$.each($verticalRulers, function(_, el) {
					$(el).remove();
				});
				
				this.verticals.length = 0;
				this.horizontals.length = 0;
			},
			
			isInitial: function() {
				var $horizontalRuler = $("#presentation").find(".ruler-wrapper.horizontal");
				var isInitial = false;
				
				$.each($horizontalRuler, function(_, ruler) {
					if ($(ruler).hasClass("initial")) {
						isInitial = true;
						return false;
					}
				});
				
				return isInitial;
			}
		};
	
	var pageTop = 0,
		offsetTop = $(".ic_page.ic_main").offset().top - $("#presentation").offset().top;
	
	$('#content').bind('scroll', function() {
	    var $element = $('#content').find('.ps-scrollbar-y-rail');
		pageTop = parseInt($element.css('top'), 10);
		
		$('#presentation').find('.ruler-wrapper.initial').css('top', pageTop);
	});
	
	var startPosition,
		$clickedElement,
		optionsHorizontal = {
		containment: "#presentation",
		axis: "y",
		scroll: false,
		start: function(event, ui) {
			$("#editorContainer").append( '<div id="horizontalRulerInfo"></div>' );
			startPosition = ui.position.top;
		},
		drag: function(event, ui) {
			var top = ui.position.top + 1 + $("#presentation").offset().top - $(".ic_page.ic_main").offset().top + "px";
			var infoValue = ui.position.top > -2 ? top : "---";
		
			$("#horizontalRulerInfo").html(infoValue);
			$("#horizontalRulerInfo").css({top: event.pageY + 2, left: event.pageX + 20});
		},
		stop: function(event, ui) {
			var rulersVisibility = !$('#rulersVisibilityButton').hasClass("disabled");
			$("#horizontalRulerInfo").remove();
			
			if(startPosition - pageTop === 0 && rulers.canAddNewHorizontal() && ui.position.top !== 0) {
				$(this).removeClass('initial');
				addRulerToHorizontalFrame(rulersVisibility);
			} else if (ui.position.top <= 0 && startPosition !== 0 && rulers.getHorizontalLength() > 0 && rulers.canAddNewHorizontal()) {
				rulers.removeHorizontal($(this), startPosition);
			} else if(ui.position.top <= 0 && startPosition !== 0 && rulers.getHorizontalLength() === 40 && rulers.canRemoveHorizontal()) {
				rulers.removeHorizontal($(this), startPosition);
			}
			
			rulers.update();
		} 
	};
	
	var optionsVertical = {
		containment: "#presentation",
		axis: "x",
		scroll: false,
		start: function(event, ui) {
			$("#editorContainer").append('<div id="verticalRulerInfo"></div>');
			
			startPosition = ui.position.left;
		},
		drag: function(event, ui) {
			var infoValue = ui.position.left > -2 ? ui.position.left + "px" : "---";
			
			$("#verticalRulerInfo").html(infoValue);
			$("#verticalRulerInfo").css({top: event.pageY - 26, left: event.pageX + 2});
		},
		stop: function(event, ui) {
			var rulersVisibility = !$('#rulersVisibilityButton').hasClass("disabled");
			$("#verticalRulerInfo").remove();

			if (startPosition === 0 && ui.position.left !== 0 && rulers.canAddNewVertical()) {
				addRulerToVerticalFrame(rulersVisibility);
			} else if(ui.position.left <= 0 && startPosition !== 0 && rulers.getVerticalLength() > 0 && rulers.canAddNewVertical()) {
				rulers.removeVertical($(this), startPosition);
			} else if(ui.position.left <= 0 && startPosition !== 0 && rulers.getVerticalLength() === 40 && rulers.canRemoveVertical()) {
				rulers.removeVertical($(this), startPosition);
			}
			
			if(ui.position.left < 0 && startPosition === 0) {
				rulers.removeVertical($(this), startPosition);
			}
			
			rulers.update();
		}
	};
	
	window.iceChangeRulerPosition = function(positionClickedRuler, position) {
		var position = parseInt(position, 10),
			rulersVisibility = !$('#rulersVisibilityButton').hasClass("disabled"),
			offset = $(".ic_page.ic_main").offset().top - $("#presentation").offset().top;
		
		if (positionClickedRuler === "horizontal") {
			if ($clickedElement.hasClass("initial") && rulers.canAddNewHorizontal() && position !== offset) {
				addRulerToHorizontalFrame(rulersVisibility, 0);
			} else if($clickedElement.position().top !== 0 && position === offset && rulers.isInitial()) {
				rulers.removeHorizontal($clickedElement, $clickedElement.position().top);
			}

			$clickedElement.css('top', position -1 +  $(".ic_page.ic_main").offset().top - $("#presentation").offset().top + 'px');
		} else {
			if ($clickedElement.position().left === 0 && rulers.canAddNewVertical() && position !== 0) {
				addRulerToVerticalFrame(rulersVisibility, 0);
				$clickedElement.css('left', position + 'px');
			} else if($clickedElement.position().left !== 0 && !rulers.canAddNewVertical() && position === 0) {
				$clickedElement.css('left', position + 'px');
			} else if($clickedElement.position().left !== 0 && rulers.canAddNewVertical() && position === 0) {
				rulers.removeVertical($clickedElement, $clickedElement.position().left);
			}
			$clickedElement.css('left', position + 'px');
		}
		
		rulers.update();
	};
	
	window.iceInitSavedRulers = function(isVisible, verticals, horizontals) {
		rulers.clear();
		
		for (var i = 0; i < verticals.length; i++) {
			addRulerToVerticalFrame(isVisible, verticals[i]);
		}
		
		for (var i = 0; i < horizontals.length; i++) {
			addRulerToHorizontalFrame(isVisible, horizontals[i]);
		}

		if (horizontals.indexOf(0) === -1 && horizontals.length < 40) {
			addRulerToHorizontalFrame(isVisible, 0);
		}
		
		if ($('#rulersVisibilityButton').hasClass("disabled")) {
			$('.ruler-wrapper').draggable('disable');
			$('.ruler-wrapper').css('display', 'none');
		} else {
			$('.ruler-wrapper').draggable('enable');
			$('.ruler-wrapper').css('display', 'block');
		}
		
		rulers.update();
	};
	
	function addRulerToHorizontalFrame(isVisible, top) {
		var visibility = isVisible ? "visible" : "",
			$divElement = $("<div/>");

		$divElement.addClass("ruler-wrapper horizontal");
		$divElement.append('<div class="ruler horizontal ' + visibility + '"></div>');
		top ? $divElement.css('top', parseInt(top, 10) + 'px') : "";
		
		$("#presentation").append($divElement);
		
		$divElement.off('draggable');
		$divElement.draggable(optionsHorizontal);
		
		$divElement.off('dblclick');
		$divElement.dblclick(function(e) {
			 positionClickedRuler = "horizontal";
			 $clickedElement = $(this);
			 var elementTop = $(this).css("top");
			 elementTop = elementTop.replace("px", "");
			 var value = elementTop - $(".ic_header.ic_page").height();/*- $(".ic_page.ic_main").offset().top - $("#presentation").offset().top*/;
			 iceShowRulerPositionModal(positionClickedRuler, value);
		});
	}
	
	function addRulerToVerticalFrame(isVisible, left) {
		var visibility = isVisible ? "visible" : "",
			$divElement = $("<div/>");
		
		$divElement.addClass("ruler-wrapper vertical");
		$divElement.append('<div class="ruler vertical ' + visibility + '"></div>');
		left ? $divElement.css('left', parseInt(left, 10) + 'px') : "";
		
		$("#presentation").append($divElement);
		
		$divElement.off('draggable');
		$divElement.draggable(optionsVertical);
		
		$divElement.off('dblclick');
		$divElement.dblclick(function(e) {
			positionClickedRuler = "vertical";
			$clickedElement = $(this);
			value = $(this).css("left");
			value = value.replace("px", "");
			iceShowRulerPositionModal(positionClickedRuler, value);
		});
	}

	/* RULERS VISIBILITY*/
	$("#rulersVisibilityButton").click(function(){
		$(this).toggleClass("disabled");
		$(".ruler").toggleClass("visible");
		
		if ($(this).hasClass("disabled")) {
			$('.ruler-wrapper').draggable('disable');
			$('.ruler-wrapper').css('display','none');
		} else {
			$('.ruler-wrapper').draggable('enable');
			$('.ruler-wrapper').css('display','block');
		}
		
		iceChangeRulersVisibility(!$(this).hasClass("disabled"));
	});
	
	/* RULERS SNAPPING */
	$("#rulersSnappingButton").click(function(){
		$(this).toggleClass("disabled");
		
		snapItems[2] = $(this).hasClass("disabled") ? undefined  : ".ruler";

		draggingOptions.snap = makeString(snapItems[0], snapItems[1], snapItems[2]);
		
		$(".moduleSelector").each(function (_, element) {
			initModuleSelector($(element));
        });
		
		iceShouldSnappingToRulers(!$(this).hasClass("disabled"));
	});
	
    // GRID VISIBILITY & WIDTH
    window.iceAdjustGridView = function() {
    	var eyeSize = $("#gridWidthButton").val();
    	
		$(".gridLine").remove();
		gridOn(eyeSize);
    };
    
	var gridVisibility = false;
	
	function gridOn(eyeSize) {
		var visibleClass;

		gridEyeSize = eyeSize;
		
		gridVisibility ? visibleClass = " visible" : visibleClass = "";
		
		var width = parseInt($(".ic_main").css("width"), 10),
			height = parseInt($(".ic_main").css("height"), 10),
			i;

		for(i = 0; i <= width/eyeSize; i++) {
			$(".ic_main").append('<div class="gridLine vertical' + visibleClass + '" style="left: '+ i * eyeSize+'px"></div>');
		}

		for(i = 0; i <= height/eyeSize; i++) {
			$(".ic_main").append('<div class="gridLine horizontal' + visibleClass + '" style="top: '+ i * eyeSize+'px"></div>');
		}
	}

	gridOn(20);
	
	// This function allows restore the modes such as 'Grid Visibility' or 'Module To Grid Snapping' while the editor is started
	window.iceTriggerClick = function(button) {
		switch(button) {
			case "gridSnapping":
				$("#gridSnappingButton").trigger("click");
				break;
			case "gridVisibility":
				$("#gridVisibilityButton").trigger("click");
				break;
			case "rulersVisibility":
				$("#rulersVisibilityButton").trigger("click");
				break;
			case "rulersSnapping":
				$("#rulersSnappingButton").trigger("click");
				break;
		}
	};
	
	$("#gridVisibilityButton").click(function(){
		$(this).toggleClass("disabled");
		$(".gridLine").toggleClass("visible");
		
		gridVisibility = !$(this).hasClass("disabled");
		
		iceChangeGridVisibility(gridVisibility);
	});
	
	$("#gridWidthButton").keyup(function() {
		$(this).val($(this).val().replace(/\D/g,''));
	});
	
	$("#gridWidthButton").blur(function() {
		$(this).val($(this).val().replace(/\D/g,''));
	});
	
	$("#gridWidthButton").change(function(){
		
		$(this).val($(this).val().replace(/\D/g,''));
		
		if (parseInt($(this).val(), 10) < 2 || $(this).val().length == 0) {
			$(this).val("2");
		}
		
		$(".gridLine").remove();
		gridOn($(this).val());
		
		$(".moduleSelector").each(function (_, element) {
			initModuleSelector($(element));
		});

		iceChangeGridSize($(this).val());
	});
	
	window.iceSetGridEyeSize = function(eyeSize) {
		gridOn(eyeSize);
	};
	
	window.iceGridOn = function(size) {
		$(".gridLine").remove();
		gridOn(parseInt(size, 10));
	};
	
	//GRID SNAPPING
	$("#gridSnappingButton").click(function(){
		$(this).toggleClass("disabled");
		
		snapItems[1] = $(this).hasClass("disabled") ? undefined : ".gridLine";
		
		draggingOptions.snap = makeString(snapItems[0],snapItems[1],snapItems[2]);
		resizingOptions.snap = makeString(snapItems[0],snapItems[1],snapItems[2]);

		isSnappingMode = !$(this).hasClass("disabled");

		$(".moduleSelector").each(function (_, element) {
			initModuleSelector($(element));
		});
		
		iceShouldSnappingToGrid(!$(this).hasClass("disabled"));
	});
	
	$('.controlsBtn').on('click', function () {
		if($(this).text() == 'Apply'){
			window.iceEditorApplication.PropertyValueHandler.keysEnabled = false;
		}
	});
	
	function getSelectedText() {
	    var text = "";
	    if (typeof window.getSelection != "undefined") {
	        text = window.getSelection().toString();
	    } else if (typeof document.selection != "undefined" && document.selection.type == "Text") {
	        text = document.selection.createRange().text;
	    }
	    return text;
	}
	
	$('#rightCol').on('mouseup', function() {
		if(getSelectedText()){
			window.offKeyboardEventsCallback();
		}else{
			window.onKeyboardEventsCallback();
		}
	});
};

//In this function implement definition of methods that are called after editor is initialized
$(document).ready(function () {
    window.jQueryManager = new window.iceEditorApplication.jQueryManager();
    window.ColorPicker = new window.iceEditorApplication.ColorPicker();

    window.cleanModuleSelectorsHandlers = function () {
        window.jQueryManager.cleanAll();
    };

	var $body = $('body'),
		position,
		clickPosition;
	
	// Header title and additional info
	$body.on("click", "#additionalHeaderItemsExpandBtn", function() {
		$(this).toggleClass("expanded");
		$(".additionalHeaderItems").toggle("fast");
	});
	
	// Header menu buttons
	$body.on("mouseenter", "a.dropDownArrow", function(){
		$(this).parent().find('a.dropDownButton').show("fast");
	});
	$body.on("mouseleave", "div.headerButton", function(){
		$(this).parent().find('a.dropDownButton').hide("fast");
	});
	
	// Left column boxes
	$body.on('click', '.expandBtn-pages', function() {
		$(this).toggleClass("expanded");
		$(".boxContents-pages").toggle("fast");
	});
	$body.on('click', '.expandBtn-modules', function() {
		$(this).toggleClass("expanded"); 
		$(".boxContents-modules").toggle("fast");
	});
	$body.on('click', '.expandBtn-assets', function() {
		$(this).toggleClass("expanded");
		$(".boxContents-assets").toggle("fast");
	});
	
	// Pages chapter expansion handling
	$body.on('click', '.pagesList .listChapter.expanded > .chapterName > .expandChapterBtn', function () {
		var $chapter = $(this).parent().parent();

		$chapter.removeClass('expanded');
		$chapter.find('.listChapter.expanded').removeClass('expanded');
		$chapter.find('.listChapter, .listItem').css('display', 'none');
	});
	
	$body.on('click', '.pagesList .listChapter:not(.expanded) > .chapterName > .expandChapterBtn', function () {
		var $chapter = $(this).parent().parent();

		$chapter.addClass('expanded');
		
		$chapter.children('.listChapter, .listItem').css('display', 'block');
	});
	
	$body.on('click', '.pagesList .listChapter.expanded > .chapterName > .expandChapterBtn', function () {
		var $chapter = $(this).parent().parent();

		$chapter.removeClass('expanded');
		$chapter.find('.listChapter.expanded').removeClass('expanded');
		$chapter.find('.listChapter, .listItem').css('display', 'none');
	});
	
	$body.on('click', function(event) {
		$options = $('#ruler_vertical_options');
		
		if (event.target.id !== 'ruler_vertical') {
			if ($options.css('display') != 'none') {
				$options.hide();

                utilityObject.captureEvents(true);
			}
		}
	});
	
	$body.on('click', '#ruler_vertical', function (event) {
		var $options = $('#ruler_vertical_options');

        utilityObject.captureEvents(false);

		clickPosition = position;

		$options.css({
			'display': 'block',
			'top': event.pageY
		});
		
		$options.mouseenter(function() {
			$('.moduleSelector-resizable').resizable('disable');
		});
		
		$options.mouseleave(function() {
			$options.hide();

            utilityObject.captureEvents(true);

			$('.moduleSelector-resizable').resizable('enable');
		});
		
		$options.find('a').click(function () {

            utilityObject.captureEvents(true);

			$options.css('display', 'none');
		});

	});
	
	$body.on('click', "#ruler_vertical_options li", function(event) {
		var pos = $(this).prevAll().length+1;

		if (pos === 1) {
			iceChangePageHeight(clickPosition);
		} else {
			iceSplitPage(clickPosition);
		}
	});
	
	//OUTSTRETCH HEIGHT RULER MOUSEOVER

	$body.on('mouseenter', '#ruler_vertical', function(event) {
		var $e = $('<div id="outstretchHeightRulerInfo"></div>');
		$("#editorContainer").append($e);
		$e.css({top: event.pageY-26, left: event.pageX+2});
	});
	
	$body.on('mousemove', '#ruler_vertical', function(event) {
		var $ruler = $("#outstretchHeightRuler"),
			$rulerInfo = $("#outstretchHeightRulerInfo"),
			$presentation = $('#presentation');
		
		var presentationOffsetTop = $presentation.offset().top;
		$ruler.css({top: event.pageY - presentationOffsetTop});
		position = parseInt($("#outstretchHeightRuler").css("top"),10) + presentationOffsetTop - $(".ic_main").offset().top;

		$rulerInfo.css({top: event.pageY + 2, left: event.pageX + 20});
		var roundedPosition = parseInt(position, 10);
		$rulerInfo.html(roundedPosition + "px");
	});
	
	$body.on('mouseleave', '#ruler_vertical', function(event) {
		$("#outstretchHeightRuler").css({top: -1});
		$("#outstretchHeightRulerInfo").remove();
	});

	function showModuleResizers($moduleSelectorElement) {
		$moduleSelectorElement.find('.moduleResizer').css('display', 'block');
	}
    
    window.iceHideModuleSelectors = function () {
    	$('.moduleResizer').css('display', 'none');
    };
    
	// INIT MODULE SELECTOR

    window.setModuleSelectorSelected = function(moduleID, shouldSelect) {
    	$('.moduleSelector').removeClass("selected");
    	
    	if (moduleID != null) {
    		
    		if(checkIfIDHasApostrophe(moduleID)) {
        		var module = document.getElementById(moduleID);
            	var $moduleSelector = $(module).next();
    		} else {
            	var $moduleSelector = $("[id='" + moduleID + "']").next();
    		}
        	
        	shouldSelect ? $moduleSelector.addClass("selected") : $moduleSelector.removeClass("selected");
    	}
    };

	window.initModuleSelector = function handleModuleSelector($moduleSelector) {
        function hideModuleResizers() {
			$moduleSelector.find('.moduleResizer').css('display', 'none');
		}

		function sendModuleSelectedInfo(moduleID, clearSelection) {
			window.selectedModuleID = moduleID;

			if (iceModuleSelected && moduleID !== undefined) {
				iceModuleSelected(moduleID, clearSelection);
			}
		}

        window.jQueryManager.add($moduleSelector);

		var resizingGridMode = false;

		$moduleSelector.off('click');
		$moduleSelector.click(function (event) {
			event.preventDefault();
			event.stopPropagation();
			iceHideModuleSelectors();
			showModuleResizers($(this));

			var $module = $(event.target).prev();
			sendModuleSelectedInfo($module.attr('id'), !event.shiftKey);
		});
		
		$moduleSelector.off('dblclick');
		$moduleSelector.on('dblclick',function (event) {
			event.preventDefault();
			event.stopPropagation();
			
			var $module = $(event.target).prev();

			iceShowModuleEditor($module.attr('id'));
		});

		$moduleSelector.on("mouseenter", function() {
			showModuleResizers($(this));
		});

		$moduleSelector.on("mouseleave", function() {
			if ($(this).attr('data-id') !== window.selectedModuleID) {
				hideModuleResizers();
			}
		});

		function addSelectorListeners ($moduleSelector) {
            $moduleSelector.addClass('moduleSelector-resizable');
            $moduleSelector.attr('data-id', $moduleSelector.prev().attr('id'));

            var $moduleInfo = null,
                startResizePosition = {};

            function getResizeDeltas(ui, $module) {
                var deltaTop = ($module.position().top - startResizePosition.top),
                    deltaLeft = ($module.position().left - startResizePosition.left),
                    deltaRight = -($module.position().left + $module.width() - startResizePosition.right),
                    deltaBottom = -($module.position().top + $module.height() - startResizePosition.bottom);

                if (!resizingGridMode) {
                    deltaTop = Math.floor(ui.position.top) - Math.floor(startResizePosition.top);
                    deltaLeft = Math.floor(ui.position.left) - Math.floor(startResizePosition.left);
                    deltaRight = -(Math.floor(ui.position.left) + $module.width() - Math.floor(startResizePosition.right));
                    deltaBottom = -(Math.floor(ui.position.top) + $module.height() - Math.floor(startResizePosition.bottom));
                }

                return {'top': deltaTop, 'left': deltaLeft, 'right': deltaRight, 'bottom': deltaBottom};
            }

            var calculateRecoupPosition = function(el, ui) {
                var left = parseInt(el.prev().css('left'),10),
                    top = parseInt(el.prev().css('top'),10),
                    recoupLeft, recoupTop;

                left = isNaN(left) ? 0 : left;
                top = isNaN(top) ? 0 : top;
                recoupLeft = left - ui.position.left;
                recoupTop = top - ui.position.top;

                return {left: recoupLeft, top: recoupTop};
            };

            var recoupPosition;

            resizingOptions = $moduleSelector.resizable({
                grid: function () {
                    var $module = $moduleSelector.prev();

                    if ($module.length == 0 || !isSnappingMode) {
                        return false;
                    }

                    var left = $module.position().left,
                        top = $module.position().top,
                        bottom = top + $module.height(),
                        right = left + $module.width();

                    if (left / gridEyeSize % 1 === 0 && top / gridEyeSize % 1 === 0
                        && bottom / gridEyeSize % 1 === 0 && right / gridEyeSize % 1 === 0) {
                        resizingGridMode = true;

                        return [gridEyeSize, gridEyeSize];
                    }

                    resizingGridMode = false;

                    return false;
                }(),
                handles: {
                    'n': $moduleSelector.find('.moduleResizer.top.center'),
                    'e': $moduleSelector.find('.moduleResizer.middle.right'),
                    's': $moduleSelector.find('.moduleResizer.bottom.center'),
                    'w': $moduleSelector.find('.moduleResizer.middle.left'),
                    'ne': $moduleSelector.find('.moduleResizer.top.right'),
                    'se': $moduleSelector.find('.moduleResizer.bottom.right'),
                    'nw': $moduleSelector.find('.moduleResizer.top.left'),
                    'sw': $moduleSelector.find('.moduleResizer.bottom.left')
                },

                start: function (event, ui) {
                    var $module = $(event.target).prev();
                    if(window.isModuleLocked($module.attr('id'))){
                    	return false;
                	}
                	
                    recoupPosition = calculateRecoupPosition($(this), ui);
                    $moduleInfo = $('<div id="moduleInfo"></div>');
                    $("#editorContainer").append($moduleInfo);

                    iceHideModuleSelectors();
                    showModuleResizers($(this));

                    $(".moduleSelector").each(function (_, moduleSelector) {
                        var $moduleSelector = $(moduleSelector);
                        $moduleSelector.off("mouseenter");
                    });

                    sendModuleSelectedInfo($module.attr('id'), true);
                    window.isModuleInAction = true;

                    startResizePosition = {
                        left: $module.position().left,
                        top: $module.position().top,
                        right: $module.position().left + $module.width(),
                        bottom: $module.position().top + $module.height()
                    };

                    var moduleBorderWidth = $module.css('border-left-width');
                    moduleBorder = parseInt(moduleBorderWidth, 10);

                    widthPadding = $(event.target).width() - $module.width();
                    heightPadding = $(event.target).height() - $module.height();
                },

                resize: function (event, ui) {
                    var $module = $(event.target).prev(),
                        resizeDeltas = getResizeDeltas(ui, $module),
                        leftDelta = null, topDelta = null, rightDelta = null, bottomDelta = null,
                        newWidth, newHeight, moduleWidth, moduleHeight;
                    if(window.isModuleLocked($module.attr('id'))){
                    	return false;
                	}

                    if ($module.css('box-sizing') == 'border-box') {
                        $module.css({
                            top: ui.position.top + recoupPosition.top,
                            left: ui.position.left + recoupPosition.left,
                            width: $(event.target).outerWidth() + (moduleBorder * 2),
                            height: $(event.target).outerHeight() + (moduleBorder * 2)
                        });
                        moduleWidth = $module.outerWidth();
                        moduleHeight = $module.outerHeight();
                    } else {
                        $module.css({
                            top: ui.position.top + recoupPosition.top,
                            left: ui.position.left + recoupPosition.left,
                            width: $(event.target).outerWidth() - widthPadding,
                            height: $(event.target).outerHeight() - heightPadding
                        });
                        moduleWidth = $module.width();
                        moduleHeight = $module.height();
                    }

                    if (isPropertyChecked($module, "left")) {
                        leftDelta = resizeDeltas.left;
                    }

                    if (isPropertyChecked($module, "top")) {
                        topDelta = resizeDeltas.top;
                    }

                    if (isPropertyChecked($module, "right")) {
                        rightDelta = resizeDeltas.right;
                    }

                    if (isPropertyChecked($module, "bottom")) {
                        bottomDelta = resizeDeltas.bottom;
                    }

                    newHeight = parseInt(moduleHeight, 10);
                    newWidth = parseInt(moduleWidth, 10);

                    $moduleInfo.html(newWidth + "px, " + newHeight + "px");
                    $moduleInfo.css({top: event.pageY + 2, left: event.pageX + 20});

                    iceModuleDimentionsChanged(newHeight, newWidth, leftDelta, topDelta, rightDelta, bottomDelta, false);
                },

                stop: function (event, ui) {
                    var $module = $(event.target).prev(),
                        resizeDeltas = getResizeDeltas(ui, $module),
                        leftDelta = null, topDelta = null, rightDelta = null, bottomDelta = null,
                        newWidth, newHeight;
                    if(window.isModuleLocked($module.attr('id'))){
                    	return false;
                	}

                    if ($module.css('box-sizing') == 'border-box') {
                        var moduleWidth = $module.outerWidth();
                        var moduleHeight = $module.outerHeight();

                    } else {
                        var moduleWidth = $module.width();
                        var moduleHeight = $module.height();

                    }

                    if (isPropertyChecked($module, "left")) {
                        leftDelta = resizeDeltas.left;
                    }

                    if (isPropertyChecked($module, "top")) {
                        topDelta = resizeDeltas.top;
                    }

                    if (isPropertyChecked($module, "right")) {
                        rightDelta = resizeDeltas.right;
                    }

                    if (isPropertyChecked($module, "bottom")) {
                        bottomDelta = resizeDeltas.bottom;
                    }

                    newHeight = parseInt(moduleHeight, 10);
                    newWidth = parseInt(moduleWidth, 10);

                    $moduleInfo.html(newWidth + "px, " + newHeight + "px");
                    $moduleInfo.css({top: event.pageY + 2, left: event.pageX + 20});

                    iceModuleDimentionsChanged(newHeight, newWidth, leftDelta, topDelta, rightDelta, bottomDelta, true);

                    $moduleSelector.on("mouseenter", function (event) {
                        showModuleResizers($(this));

                        var $module = $(event.target).prev();
                        sendModuleSelectedInfo($module.attr('id'), true);
                    }),

                        $moduleInfo.remove();
                    window.isModuleInAction = false;
                }
            });

			var startDragPosition = {};

			function getDragDeltas(ui) {
				return {
					'top': Math.floor(ui.top) - Math.floor(startDragPosition.top),
					'left': Math.floor(ui.left) - Math.floor(startDragPosition.left),
					'right': - (Math.floor(ui.left) - Math.floor(startDragPosition.left)),
					'bottom': - (Math.floor(ui.top) - Math.floor(startDragPosition.top))
				};
			}

			draggingOptions = $moduleSelector.draggable({
				snap: makeString(snapItems[0],snapItems[1],snapItems[2]),
				snapTolerance: 10,
				start: function (event, ui) {
					var $module = $(event.target).prev();
					if ($module.css('display') == 'none') {
						$module.css('display','');
						$module.css('visibility', 'hidden');
					}
                    if(window.isModuleLocked($module.attr('id'))){
                    	return false;
                	}
					
                    recoupPosition = calculateRecoupPosition($(this), ui);
					$("#editorContainer").append('<div id="moduleInfo"></div>');
					iceHideModuleSelectors();
					showModuleResizers($(event.target));

					sendModuleSelectedInfo($module.attr('id'), true);
					window.isModuleInAction = true;

					startDragPosition = {
						left: $module.position().left,
						top: $module.position().top
					}
				},
				drag: function (event, ui) {
					var $moduleInfo = $("#moduleInfo"),
						$selector = $(event.target),
						$module = $selector.prev(),
						dragDeltas = getDragDeltas({
							top: ui.position.top,
							left: ui.position.left
						}),
						leftDelta = null, topDelta = null, rightDelta = null, bottomDelta = null;
                    if(window.isModuleLocked($module.attr('id'))){
                		return false;
                	}

					var newLeft = parseInt(ui.position.left, 10);
					var newTop = parseInt(ui.position.top, 10);

					$moduleInfo.html(newLeft + "px, " + newTop + "px");
					$moduleInfo.css({top: event.pageY + 2, left: event.pageX + 20});

					$module.css({
						top: newTop + recoupPosition.top + 'px',
						left: newLeft + recoupPosition.left + 'px'
					});

					if (isPropertyChecked($module, "left")) {
						leftDelta = dragDeltas.left;
					}

					if (isPropertyChecked($module, "top")) {
						topDelta = dragDeltas.top;
					}

					if (isPropertyChecked($module, "right")) {
						rightDelta = dragDeltas.right;
					}

					if (isPropertyChecked($module, "bottom")) {
						bottomDelta = dragDeltas.bottom;
					}

					if (iceModulePositionChanged) {
						iceModulePositionChanged($module.attr('id'), leftDelta, topDelta, rightDelta, bottomDelta, false);
					}
				},

				stop: function (event, ui) {
					var $module = $(event.target).prev(),
						modulePosition = $module.position(),
						$selector = $(event.target),
						dragDeltas = getDragDeltas(modulePosition),
						leftDelta = null, topDelta = null, rightDelta = null, bottomDelta = null;
                    if(window.isModuleLocked($module.attr('id'))){
                		return false;
                	}

					if (isPropertyChecked($module, "left")) {
						leftDelta = dragDeltas.left;
					}

					if (isPropertyChecked($module, "top")) {
						topDelta = dragDeltas.top;
					}

					if (isPropertyChecked($module, "right")) {
						rightDelta = dragDeltas.right;
					}

					if (isPropertyChecked($module, "bottom")) {
						bottomDelta = dragDeltas.bottom;
					}

		            if (iceModulePositionChanged) {
		            	iceModulePositionChanged($module.attr('id'), leftDelta, topDelta, rightDelta, bottomDelta, true);
		            	iceRefreshView();
		            }

		            $("#moduleInfo").remove();
					window.isModuleInAction = false;
					
					$selector.css({
						'top': modulePosition.top,
						'left': modulePosition.left
					});

				}
			});
		}
		
		if (!$moduleSelector.hasClass('moduleSelector-locked') || window.shouldBeUnlocked) {
			addSelectorListeners($moduleSelector);
		}
		
		window.addListerToSelector = function ($moduleSelector) {
			addSelectorListeners($moduleSelector);
		};
		
		$moduleSelector.each(function () {
			var $this = $(this), $relatedElement = null;

			if ($this.hasClass('moduleSelector')) {
				$relatedElement = $this.prev();

				$this.css({
					width: $relatedElement.outerWidth(),
					height: $relatedElement.outerHeight()
				});
			}
		});
	};
	
	window.assignModuleAndSelector = function (moduleId) {
		if(checkIfIDHasApostrophe(moduleId)){
			keyModule = document.getElementById(moduleId);//$('.ic_page.ic_main').find("[id='" + moduleId + "']");
			keySelector = $(keyModule).next();
		} else {
			keyModule = $('.ic_page.ic_main').find("[id='" + moduleId + "']");
			keySelector = keyModule.next();
		}
	};
	
	window.removeAssignModuleAndSelector = function () {
		keyModule = null;
		keySelector = null;
	};
	
	function isPropertyChecked($module, property) {
		if (property === "left") {
			return $module.attr("data-relative-left");
		} else if (property === "right") {
			return $module.attr("data-relative-right");
		} else if (property === "top") {
			return $module.attr("data-relative-top");
		} else if (property === "bottom") {
			return $module.attr("data-relative-bottom");
		}
	}
	
	window.iceOnPageChanged = function () {
		var $icPage = $('.ic_page.ic_main'),
			$header = $('.ic_header'),
			$footer = $('.ic_footer'),
			height = $icPage.height();
		
		if ($header.is(':visible')) {
			height += $header.height();
		}
		
		if ($footer.is(':visible')) {
			height += $footer.height();
		}
		
		$('#presentation').css({
			'width': $icPage.width() + "px",
			'height': height + "px"
		});
		
		$(".moduleSelector").each(function (_, element) {
			initModuleSelector($(element));
        });
		
		iceHideModuleSelectors();
		
    	window.selectedModuleID = null;
	};

	window.iceOnPageSelected = function () {
		iceHideModuleSelectors();

		window.selectedModuleID = null;
	};
	
	function checkIfIDHasApostrophe (id) {
		return id.indexOf("'") > -1;
	}
	
	window.iceOnModuleChanged = function (moduleID, isSelected) {
		// Usual selector $('#<id>') will not work (it will throw exception) if
		// module ID contains spaces.
		
		if(checkIfIDHasApostrophe(moduleID)){
			var $module = document.getElementById(moduleID),// $("[id='" + moduleID + "']"),
			$moduleSelector = $($module).next();	
		} else{
			var $module = $("[id='" + moduleID + "']"),
			$moduleSelector = $module.next();
		}
		
		
		initModuleSelector($moduleSelector);

		if (isSelected) {
			showModuleResizers($moduleSelector);
		}
	};
	
	window.iceOnModuleSelected = function (moduleID) {
		// Usual selector $('#<id>') will not work (it will throw exception) if
		// module ID contains spaces.

		if(checkIfIDHasApostrophe(moduleID)){
			var $module = document.getElementById(moduleID),
			$moduleSelector = $($module).next();
		} else {
			var $module = $(".ic_page.ic_main").find("[id='" + moduleID + "']"),
			$moduleSelector = $module.next();
		}
		
		window.selectedModuleID = moduleID;
		
		iceHideModuleSelectors();
		showModuleResizers($moduleSelector);
        window.jQueryManager.setSelectedModule($module);
	};
	
	// Add modules
	$body.on("click", "#addModulePage-tabs .tabButton", function() {
		var $allTabButtons = $('#addModulePage-tabs').find('.tabButton'),
			$currentButton = $(this),
			category = $currentButton.attr('for-name'),
			$contents = $('#addModulePage-contents');
		
		$allTabButtons.removeClass('selected');
		$currentButton.addClass('selected');
		
		$contents.find('.tabContents').removeClass('visible');
		$contents.find('.tabContents[category-name="' + category + '"]').addClass('visible');

		iceUpdateScrollbars();
	});
	
	// Select file
	$body.on("click", "#filesPage .tabButton", function() {
		var $allTabButtons = $('#filesPage').find('.tabButton'),
			$currentButton = $(this),
			category = $currentButton.attr('for-name'),
			$filesPage = $('#filesPage');
		
		$allTabButtons.removeClass('selected');
		$currentButton.addClass('selected');
		
		$filesPage.find('.tabContents').css('display', 'none');
		$filesPage.find('.tabContents[type-name="' + category + '"]').css('display', 'block');

		iceUpdateScrollbars();
	});
	
	// trigger click on close button executing logic for proper window, if it's needed
	$body.on('keydown', function(e) {	
		var $visibleMainPage = $(".mainPage:visible"),
			code = e.keyCode || e.which;

		if (code == 27 && $visibleMainPage.find(".mainPageCloseBtn").length && $('#modalWrapper').is(":hidden")) { // esc + opened main page + modal is hidden
			setTimeout(function() {
				$visibleMainPage.find(".mainPageCloseBtn").trigger('click');
			}, 100);
		}
	});
	
	//close all windows excludes these with save confirmation
	$body.on("click", ".mainPage .mainPageCloseBtn", function () {
		var ids = ['textEditorPage', 'propertiesPage', 'htmlEditorPage', 'staticlistPage'], // id windows with save confirmation
			$page = $(this).closest(".mainPage");
		
		if (ids.indexOf($page.attr('id')) == -1) {
			$(this).closest(".mainPage").hide();
		}

		if ($(this).hasClass('closeWidgetLocker')) {
			// Special case of X buttons which should not close Widget Locker
			// (f.i. File Selector opened from List property) doesn't have this class.
			iceHideWidgetLocker();
			window.iceEditorApplication.PropertyValueHandler.keysEnabled = true;
		}
	});
	
	window.iceGetPageScrollTopPosition = function () {
		return parseInt($('#content').scrollTop(), 10);
	};

	window.widgetLocketVisible = false;
	
	window.iceShowWidgetLocker = function () {
		window.widgetLocketVisible = true;
		
		$('.widgetLock').fadeIn(100);
		$('#settingsBtn').hide();
	};
	
	window.iceHideWidgetLocker = function () {
		window.widgetLocketVisible = false;

		$('.widgetLock').fadeOut(100);
		$('#settingsBtn').show();
	};
	
	window.iceIsWidgetLockerVisible = function () {
		return window.widgetLocketVisible;
	};

    window.iceDetermineHTMLToolbarVisibilityInList = function () {
    	var $wrapper = $('#propertiesPage').find('.propertiesItemsListWrapper'),
    		$toolbar = $wrapper.parent().find('.gwt-RichTextToolbar'),
    		shouldBeVisible = $wrapper.find('.richTextEditArea').length > 0;
    	
    	if (shouldBeVisible) {
    		$toolbar.show();
    		$wrapper.removeClass('no-toolbar');
    	} else {
    		$toolbar.hide();
    		$wrapper.addClass('no-toolbar');
    	}
    };

	window.iceDetermineHTMLToolbarVisibilityInStaticList = function () {
    	var $wrapper = $('#staticListPage').find('.propertiesStaticItemsListWrapper'),
    		$toolbar = $wrapper.parent().find('.gwt-RichTextToolbar'),
    		shouldBeVisible = $wrapper.find('.richTextEditArea').length > 0;

    	if (shouldBeVisible) {
    		$toolbar.show();
    		$wrapper.removeClass('no-toolbar');
    	} else {
    		$toolbar.hide();
    		$wrapper.addClass('no-toolbar');
    	}
    };

    window.iceUpdateCommonsLocks = function () {
		$('#headerLock').height($('.ic_header').outerHeight());
		$('#footerLock').height($('.ic_footer').outerHeight());
	};

    window.iceFindModulesInBoundries = function (x1, y1, x2, y2) {
    	var selectedModules = [],
    		allModules = $('.ic_page.ic_main').find('.ice_module');
    	
    	selectedModules = allModules.map(function () {
    		var $this = $(this),
    			position = $this.position(),
    			top = position.top,
    			left = position.left,
    			width = $this.width(),
    			height = $this.height(),
    			right = left + width,
    			bottom = top + height;

    		// From original Editor
    		if ((left > x1 && left < x2) || (right > x1 && right < x2)) {
    			if ((top > y1 && top < y2) || (bottom > y1 && bottom < y2)) {
    				return {
    					id: $this.attr('id'),
    					left: left,
    					top: top,
    					bottom: bottom,
    					right: right
    				};
    			}
    		}

    		return null; // Module not in boundries 
    	});

		$.each(selectedModules, function (_, module) {
			$('#' + module.id).next().addClass('moduleSelector-hidden');
		});
    	
    	return selectedModules;
    };

     function isGroupIntoDiv($module){
     	if($module.get(0).parentElement.className.indexOf("modules_group") !== -1){
     		return true;
     	}
     	return false;
     }

	 function isModificatedHeight($group){
     	if($group.className.indexOf("modificated_height") !== -1){
     		return true;
     	}
     	return false;
	 }

	 function isModificatedWidth($group){
     	if($group.className.indexOf("modificated_width") !== -1){
     		return true;
     	}
     	return false;
	 }

    window.iceGetSelectedModulesBoundries = function (ids) {
    	var boundries = { top: 0, bottom: 0, left: 0, right: 0 };
    	
    	if (ids.length == 0) {
    		return boundries;
    	}
    	
    	for (var i = 0; i < ids.length; i++) {
    		// Usual selector $('#<id>') will not work (it will throw exception) if
    		// module ID contains spaces.
    		if(checkIfIDHasApostrophe(ids[i])){
    			var $module = document.getElementById(ids[i]);
    		} else {
        		var $module = $('.ic_main').find("[id='" + ids[i] + "']");
    		}

			var position = $($module).position();
			
			if (position === null) {
				// it probably means that module was removed
				continue;
			}
			
			var	top = position.top,
				left = position.left,
				width = $($module).outerWidth(),
				height = $($module).outerHeight();

            //move selector to modules position when modules have relative position
    		if(isGroupIntoDiv($module)){
    			var parent = $($module).get(0).parentElement;
    			var parentPosition = $(parent).position();
    			top = top + parentPosition.top;
    			left = left + parentPosition.left;
    			if(isModificatedWidth(parent)) {
    				width = $(parent).outerWidth();
    				left = parentPosition.left;
    			}
    			if(isModificatedHeight(parent)) {
    				height = $(parent).outerHeight();
    				top = parentPosition.top;
    			}
			}
			var right = left + width;
    		var bottom = top + height;

    		if (i == 0) {
    			boundries = {
					left: left,
					top: top,
					bottom: bottom,
					right: right
    			};
    			
    			continue;
    		}
    		
    		if (left < boundries.left) {
				boundries.left = left;
			}
			
			if (top < boundries.top) {
				boundries.top = top;
			}
			
			if (bottom > boundries.bottom) {
				boundries.bottom = bottom;
			}
			
			if (right > boundries.right) {
				boundries.right = right;
			}
    	}
    	
    	return boundries;
    };
    
    window.iceShowHiddenModuleSelectors = function () {
    	$('.moduleSelector-hidden').removeClass('moduleSelector-hidden');
    };
    
	window.shouldDisableDrag = function (shouldDisableDragging) {
		if (shouldDisableDragging) {
			$(".moduleSelector").draggable('disable');
		} else {
			$(".moduleSelector").draggable('enable');
		}
	};

    // Drag the group of modules
	window.makeDraggable = function(moduleIds) {
		var startModulesPositions = [],
            startModulesPositionsKeyPress = [],
            uiPositionStart = {},
            selectors = [],
			groups = [],
			startGroupPositions = [],
            movements = [];
            modules = [];
            ids = moduleIds;

        function calculateRecoupPosition($module, $selector) {
            var left = parseInt($module.css('left'), 10),
                top = parseInt($module.css('top'), 10),
                recoupLeft, recoupTop;

            left = isNaN(left) ? 0 : left;
            top = isNaN(top) ? 0 : top;

            recoupLeft = left - parseInt($selector.css('left'), 10);
            recoupTop = top - parseInt($selector.css('top'), 10);

            return {left: recoupLeft, top: recoupTop};
        }

        // Push all modules and modules ids selectors to arrays.
        for (var i = 0; i < ids.length; i++) {
            var moduleID = ids[i],
                $page = $('#presentation').find('.ic_page.ic_main');

            modules.push($page.find('[id="' + moduleID + '"]'));
            selectors.push($page.find('[data-id="' + moduleID + '"]'));
        }

        // Move all modules and selectors during dragging
		function onModulesSelectorPositionChanged(uiEvent, submit, addToHistory) {
			var left = uiPositionStart.left - uiEvent.position.left,
	    		top = uiPositionStart.top - uiEvent.position.top,
	    		$module, $moduleSelector, moduleStartPosition,
	    		moduleTop, moduleLeft, right, bottom;
	        
	        for (var i = 0; i < modules.length; i++) {
	        	$module = modules[i];
	        	moduleStartPosition = startModulesPositions[i];
	        	if(window.isModuleLocked($module.attr("id"))){
	        		continue;
	        	}

	        	//ignore modules into div
	        	if(isDisableClass($module)){
	        		continue;
				}

	        	moduleTop = moduleStartPosition.top - top;
	        	moduleLeft = moduleStartPosition.left - left;

                $moduleSelector = $module.next() || selectors[i];
                $moduleSelector.css({
                    top: moduleTop,
                    left: moduleLeft
                });

	            $module.css({
	            	top: moduleTop + movements[i].top + 'px',
	            	left: moduleLeft + movements[i].left + 'px'
	            });

	        	//only delta of moving is important, not right or bottom but them movement
	        	right = left;
	        	bottom = top;
	        	
	            if (iceModulePositionChanged) {
	            	if(i == (modules.length -1) && addToHistory) {
	            		iceModulePositionChanged(ids[i], -left, -top, right, bottom, submit, true);
	            	}else{
	            		iceModulePositionChanged(ids[i], -left, -top, right, bottom, submit, false);
	            	}
	            }
	        }

            // Refresh view on stop of dragging action
	        if(submit){
	        	iceRefreshView();
	        }        
		}

		//move all groups modules into div
		function onGroupPositionChanged(uiEvent, submit, addToHistory) {
			var left = uiPositionStart.left - uiEvent.position.left,
	    		top = uiPositionStart.top - uiEvent.position.top,
	    		$group, startPosition,
	    		groupTop, groupLeft, right, bottom;

	        for (var i = 0; i < groups.length; i++) {
	        	$group = groups[i];
	        	startPosition = startGroupPositions[i];

	        	groupTop = startPosition.top - top;
	        	groupLeft = startPosition.left - left;


	            $group.css({
	            	top: groupTop + 'px',
	            	left: groupLeft + 'px'
	            });


	        	var idGroup = $group.get(0).id;
	            if (iceModulePositionChanged) {
	            	if(addToHistory) {
	            		iceModulePositionChanged(idGroup, groupLeft, groupTop, null, null, submit, true);
	            	}else{
	            		iceModulePositionChanged(idGroup, groupLeft, groupTop, null, null, submit, false);
	            	}
	            }
	        }

	        if(submit){
	        	iceRefreshView();
	        }
		}

		$('.multipleModuleSelector').draggable({
			snap: makeString(snapItems[0],snapItems[1],snapItems[2]),
			snapTolerance: 10,
			start: function(event, ui) {
                utilityObject.captureEvents(false);

                $("#editorContainer").append('<div id="moduleInfo"></div>');

				uiPositionStart = {
					top: ui.position.top,
					left: ui.position.left
				};

                groups = [];
                startGroupPositions = [];
                var blockedModules = [];
				for (var i = 0; i < ids.length; i++) {
	            	if(isGroupIntoDiv(modules[i])) {
	            		var $parent = $(modules[i].get(0).parentElement);
	            		if(!containsElement(groups, $parent)) {
                            groups.push($parent);
                            startGroupPositions.push({top: $parent.position().top, left: $parent.position().left});
                        }

                        //blocked modules into div
                        if (!isDisableClass(modules[i])){
                            blockedModules.push(modules[i]);
						}
					}
	            }
                disableModuleIntoGroup(blockedModules);
                startModulesPositions.length = 0;
	            for (var i = 0; i < ids.length; i++) {
	            	startModulesPositions.push({top: modules[i].position().top, left: modules[i].position().left});
	            	movements[i] = calculateRecoupPosition(modules[i], selectors[i]); // If some element has rotation its top and left values are incompatible with selector
	            }
			},

			drag: function(event, ui) {
				var $moduleInfo = $("#moduleInfo"),
					left = parseInt(ui.position.left, 10),
					top = parseInt(ui.position.top, 10);

				$moduleInfo.html(left + "px, " + top + "px");
				$moduleInfo.css({top: event.pageY + 2, left: event.pageX + 20});

	            onModulesSelectorPositionChanged(ui, false, false);
	            onGroupPositionChanged(ui,false, false);
			},
			
			stop: function(_, ui) {
				$("#moduleInfo").remove();
				onModulesSelectorPositionChanged(ui, true, true);
				onGroupPositionChanged(ui, true, true);
                utilityObject.captureEvents(true);
			}
		});

        function disableModuleIntoGroup(elements){
        	  for(var i = 0; i < elements.length; i++){
				    elements[i].next().addClass("ui-state-disabled");
	            }
		}

        function isDisableClass($module){
        	  var $moduleSelector = $module.next();
        	  if ($moduleSelector.hasClass('ui-state-disabled')) {
        	  	return true;
			  }
			  return false;
        }

        function containsElement(list, $elem) {
        	for(var i = 0; i < list.length; i++){
        		if(list[i].get(0).id === $elem.get(0).id){
        			return true;
				}
			}
            return false;
        }

		for (var i = 0; i < ids.length; i++) {
        	startModulesPositionsKeyPress.push({top: modules[i].position().top, left: modules[i].position().left});
        }
		
		function onKeyPressSelectorPositionChanged(uiEvent, submit) {
			var cFire = new Date();
			
			if(window.iceEditorApplication.PropertyValueHandler.keysEnabled){
				if ((cFire - lastFire) / 1000 > 1/7){
					var left = uiEvent.position.left,
			    		top = uiEvent.position.top,
			    		$module, moduleStartPosition, right, bottom, anyModuleMoved = false;
		
			        for (var i = 0; i < modules.length; i++) {
			        	var moduleID = ids[i];
			        	
			        	$module = modules[i];
			        	moduleStartPosition = startModulesPositionsKeyPress[i];
			            if(window.isModuleLocked($module.attr('id')) || checkIfMainPageOpened()){
			        		continue;
			        	}
			        	
			            anyModuleMoved = true;
			            
			        	var currentModuleTop = parseInt($($module).css('top').replace('px', ''), 10),
			        		currentModuleLeft = parseInt($($module).css('left').replace('px', ''), 10);			        	
			        	
			            $module.css({
			            	top: currentModuleTop + uiEvent.position.top + 'px',
			            	left: currentModuleLeft + uiEvent.position.left+ 'px'
			            });
			        	$moduleSelector = $module.next() || selectors[i];
			        	
			        	$moduleSelector.css({
			        		top: currentModuleTop + uiEvent.position.top + 'px',//moduleTop,
			        		left: currentModuleLeft + uiEvent.position.left+ 'px'//moduleLeft
			        	});
		
			        	//only delta of moving is important, not right or bottom but them movement
			        	right = left;
			        	bottom = top;
			        	
			            if (iceModulePositionChanged) {
			            	if(i == (modules.length - 1)){
			            		iceModulePositionChanged(moduleID, left, top, right, bottom, submit, true);
			            	}else{
			            		iceModulePositionChanged(moduleID, left, top, right, bottom, submit, false);
			            	}
			            }
			        }
			        
			        var currentMulSelTop = parseInt($('.multipleModuleSelector').css('top').replace("px", ""));
			        var currentMulSelLeft = parseInt($('.multipleModuleSelector').css('left').replace("px", ""));
			        
			        if(anyModuleMoved) {
				        $('.multipleModuleSelector').css({
				        	top: currentMulSelTop + uiEvent.position.top + 'px',
				        	left: currentMulSelLeft + uiEvent.position.left+ 'px'
				        });
			        }
			        lastFire = cFire;
				}
			}
		}
		
		if(!initializedEvent){
			window.iceEditorApplication.PropertyValueHandler.keysEnabled = true;
			$(document).on('keydown', function (e) {
				if($('.multipleModuleSelector').length != 0){
					var $element = $('#content')[0];
					Ps.destroy($element);//disable scrolling content
					keyModule = null;
					keySelector = null;
					//up arrow
					if( e.which === 38 && e.shiftKey ) {
						  var uiEvent = { position: { left: 0, top: -10}};
						  onKeyPressSelectorPositionChanged(uiEvent, true);
					}else if(e.which == 38){
						  var uiEvent = { position: { left: 0, top: -1}};
						  onKeyPressSelectorPositionChanged(uiEvent, true);
					}
					
					//down arrow
					if( e.which === 40 && e.shiftKey ) {
						var uiEvent = { position: { left: 0, top: 10}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}else if(e.which == 40){
						var uiEvent = { position: { left: 0, top: 1}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}
					
					//left arrow
					if( e.which === 37 && e.shiftKey ) {
						var uiEvent = { position: { left: -10, top: 0}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}else if(e.which == 37){			  
						var uiEvent = { position: { left: -1, top: 0}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}
					
					// right arrow
					if( e.which === 39 && e.shiftKey ) {
						var uiEvent = { position: { left: 10, top: 0}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}else if(e.which == 39){
						var uiEvent = { position: { left: 1, top: 0}};
						onKeyPressSelectorPositionChanged(uiEvent, true);
					}
					Ps.initialize($element);//enable scrolling content
				}
			});
			initializedEvent = true;
		}
	};
	
	function keyUpOrDownPressed(moveValue) {
		var cFire = new Date();
				
		if ((cFire - lastFire) / 1000 > 1/8){
			var $selector = keySelector,
				$module = keyModule,
				topDelta = null,
				bottomDelta = null;
			
			var moduleTop = parseInt($($module).css('top').replace('px', ''), 10);
			$($module).css({
				top: ((moduleTop)+moveValue) + 'px'
			});
			
			$($selector).css({
				top: ((moduleTop)+moveValue) + 'px'
			});
			
			if (isPropertyChecked($module, "top")) {
				topDelta = moveValue;
			}
			
			if (isPropertyChecked($module, "bottom")) {
				bottomDelta = -moveValue;
			}
			
			if (iceModulePositionChanged) {
				iceModulePositionChanged($module.attr('id'), null, topDelta, null, bottomDelta, true);
			}
			lastFire = cFire;
		}
	}
	
	function keyLeftOrRightPressed(moveValue) {
		var cFire = new Date();
		
		if ((cFire - lastFire) / 1000 > 1/8){    
			var $selector = keySelector,
				$module = keyModule,
				leftDelta = null,
				rightDelta = null;
			
			var moduleTop = parseInt($($module).css('left').replace('px', ''), 10);
			$($module).css({
				left: ((moduleTop)+moveValue) + 'px'
			});
			
			$($selector).css({
				left: ((moduleTop)+moveValue) + 'px'
			});
			
			if (isPropertyChecked($module, "left")) {
				leftDelta = moveValue;
			}
			
			if (isPropertyChecked($module, "right")) {
				rightDelta = -moveValue;
			}
			
			if (iceModulePositionChanged) {
				iceModulePositionChanged($module.attr('id'), leftDelta, null, rightDelta, null, true);
			}
			lastFire = cFire;
		}
	}
	
	function checkIfMainPageOpened () {
		var mainPages = document.getElementsByClassName('mainPage'),
			isOpened = false;
		
		$(mainPages).each(function () {
			if($(this).css('display') == 'block') {
				isOpened = true;
			}
		});
		
		return isOpened;
	}
	
	$(document).on("keydown", function (e) {
		if(keyModule != null && keySelector != null && window.iceEditorApplication.PropertyValueHandler.keysEnabled){
			
            if(window.isModuleLocked(keyModule.attr('id')) || checkIfMainPageOpened()){
        		return;
        	}
			
			var $element = $('#content')[0];
			Ps.destroy($element); //disable scrolling content
			  
			//up arrow  
			if( e.which === 38 && e.shiftKey ) {
				  keyUpOrDownPressed(-10);
			}else if(e.which == 38){
				  keyUpOrDownPressed(-1);
			}
			  
			//down arrow
			if( e.which === 40 && e.shiftKey ) {
				keyUpOrDownPressed(10);
			}else if(e.which == 40){
				keyUpOrDownPressed(1);
			}
			
			//left arrow
			if( e.which === 37 && e.shiftKey ) {
				keyLeftOrRightPressed(-10);
			}else if(e.which == 37){			  
				keyLeftOrRightPressed(-1);
			}
			
			// right arrow
			if( e.which === 39 && e.shiftKey ) {
				keyLeftOrRightPressed(10);
			}else if(e.which == 39){
				keyLeftOrRightPressed(1);
			}
			
			Ps.initialize($element); //enable scrolling content
		}		  
	});
	
	$(document).keyup(function(e) {
		  if (e.keyCode == 27){
			  window.iceEditorApplication.PropertyValueHandler.keysEnabled = true;
		  }
	});
	
	window.executeActionOnHide = function() {
		iceExecuteActionOnHide();
	};
	
	window.executeActionOnPreview = function() {
		iceExecuteActionOnPreview();
	};

	window.initBlocklyCodeEditor = function(container, toolboxXML) {
		var workspace = Blockly.inject(container, {
            toolbox: toolboxXML,
            sounds: false
        });
		return workspace;
	}
});