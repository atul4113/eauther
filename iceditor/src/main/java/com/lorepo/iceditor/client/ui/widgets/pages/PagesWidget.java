package com.lorepo.iceditor.client.ui.widgets.pages;

import static com.google.gwt.query.client.GQuery.$;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.Node;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.Style;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.query.client.css.CSS;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.SelectionController;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class PagesWidget extends Composite {

	private static PagesWidgetUiBinder uiBinder = GWT
			.create(PagesWidgetUiBinder.class);

	interface PagesWidgetUiBinder extends UiBinder<Widget, PagesWidget> {
	}
	
	private SelectionController selectionController;
	private Content content;
	private AbstractAction	onSelectionAction;
	private IContentNode selectedNode;
	private Map<IContentNode, Element> elements = new HashMap<IContentNode, Element>();
	private Map<String, Integer> pageIndexes = new HashMap<String, Integer>();
	private Map<String, Boolean> chapterExpandedStatus = new HashMap<String, Boolean>(); // key is id
	
	private final String TAB_ACTIVE_CSS_CLASS = "active";
	private final String MAIN_ID = "pagesList-navigation";
	private final String COMMONS_ID = "pagesList-commons";
	
	@UiField HTMLPanel panel;
	@UiField DivElement main;
	@UiField DivElement commons;
	@UiField SpanElement boxTitle;
	@UiField AnchorElement mainTab;
	@UiField AnchorElement commonsTab;
	GQuery $navigation = null;
	GQuery $commons = null;
	
	public PagesWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		mainTab.addClassName(TAB_ACTIVE_CSS_CLASS);
		updateElementsTexts();
		connectHandlers();
		setPanelsID();
	}
	
	public void setSelectionController(SelectionController selectionController) {
		this.selectionController = selectionController;
	}
	
	public void setModel(Content content) {
		this.content = content;
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onSelectionAction = actionFactory.getAction(ActionType.pageSelected);
	}
	
	public void refresh() {
		elements.clear();
		pageIndexes.clear();
		refreshTableOfContents();
		refreshCommons();
		MainPageUtils.updateWidgetScrollbars("pages");
	}
			
	private void saveChapterExpandedStatus(Node parent) {
		ElementIterator elements = new ElementIterator(parent);

	    for(Element elem : elements) {
			if ( isChapter(elem) ) {
				if ( elementHasClassName(elem, "expanded") ) {
					chapterExpandedStatus.put( elem.getId(), true );
				}
				else {
					chapterExpandedStatus.put( elem.getId(), false );
				}
			}
			
			if (elem.hasChildNodes()) {
				saveChapterExpandedStatus(elem);
			}
		}
	}

	public void doExpandToSelected() {
		expandToSelected(main);	
	}
	
	private boolean isChapter(Element elem) {
		return elementHasClassName(elem, "listChapter");
	}

	private boolean isPage(Element elem) {
		return elementHasClassName(elem, "listItem");
	}
	
	private void chapterExpand(Element chapter) {
		if (elementHasClassName(chapter, "expanded") == false) {
			chapter.addClassName("expanded");
		}
	}
	
	private void setDisplayBlock(Element elem) {
		Style style = elem.getStyle();
		style.setDisplay(Display.BLOCK);
	}
	
	public static boolean elementHasClassName(Element elem, String className) {
		// doesn't do trimming of className as newer GWT does, so don't pass string with whitespaces 
		return elem.getClassName().contains(className);
	  }
	
	
	private boolean expandToSelected(Node parent) {
		ElementIterator elements = new ElementIterator(parent);

	    for(Element elem : elements) {
	    		    	
			if (elementHasClassName(elem, "selected")) {
				if (isChapter(elem)) {
					setDisplayBlock(elem);
					chapterExpand(elem);
				}

				// show all siblings
				ElementIterator elements1 = new ElementIterator(parent);
				for(Element elem1 : elements1) {
					if (isPage(elem1) || isChapter(elem1)) { // there might be other types
						setDisplayBlock(elem1);
					}
				}
				return true;
			}
			
			if (elem.hasChildNodes()) {
				boolean result = expandToSelected(elem);
				
				if (result) {
					if (isChapter(elem)) {
						setDisplayBlock(elem);
						chapterExpand(elem);
					}
					
					ElementIterator elements1 = new ElementIterator(elem);
					for(Element elem1 : elements1) {
						if (isPage(elem1)) {
							setDisplayBlock(elem1);
						}
					}
					return true;
				}
			}	    	
	    }
				
		return false;
	}
	
	public void refreshTableOfContents() {
		doExpandToSelected();
		saveChapterExpandedStatus(main);
				
		clearContainer(main);
		
		IChapter tableOfContents = this.content.getTableOfContents();
		int size = tableOfContents.size();
		int index = 0;
		
		for (int i = 0; i < size; i++) {
			IContentNode node = tableOfContents.get(i);
			
			if (node instanceof Page) {
				index++;
				addNavigationPageElement(main, (Page) node, index, false);
			} else {
				index += renderChapter(main, (IChapter) node, index, false);
			}
		}
	}
	
	private int renderChapter (DivElement container, final IChapter chapter, int index, boolean parentIsCollapsed) {

		final DivElement chapterElement = Document.get().createDivElement();

		chapterElement.setId( chapter.getId()  );
		chapterElement.setClassName("listChapter");
		
		Boolean expanded = chapterExpandedStatus.get( chapter.getId() );
				
		if (expanded != null) {
			Style style = chapterElement.getStyle();
			
			if (expanded.booleanValue() == true && parentIsCollapsed == false) {
				// it was expanded and parent is not collapsed - so make it expanded
				chapterExpand(chapterElement);
				style.setDisplay(Display.BLOCK);
			}
			else if (expanded.booleanValue() == false && parentIsCollapsed == false) {
				// it was collapsed and parent is not collapsed - so make it visible, but collapse children
				parentIsCollapsed = true;
				style.setDisplay(Display.BLOCK);
			}
			else if (expanded.booleanValue() == false || parentIsCollapsed == true) {
				style.setDisplay(Display.NONE);
			}
		}
		else { // expanded status can't be found - first time loading tree, make it expanded
			chapterExpand(chapterElement);
		}
		
		AnchorElement expandChapterButton = Document.get().createAnchorElement();
		expandChapterButton.setClassName("expandChapterBtn");
		
		DivElement chapterNameElement = Document.get().createDivElement();
		chapterNameElement.setClassName("chapterName");
		chapterNameElement.setInnerText(chapter.getName());
		chapterNameElement.appendChild(expandChapterButton);
		
		chapterElement.appendChild(chapterNameElement);
		
		int size = chapter.size();
		int addedPages = 0;
		
		for (int i = 0; i < size; i++) {
			IContentNode node = chapter.get(i);
			
			if (node instanceof Page) {
				addedPages++;
				addNavigationPageElement(chapterElement, (Page) node, index + addedPages, parentIsCollapsed);
			} else {
				addedPages += renderChapter(chapterElement, (IChapter) node, index + addedPages, parentIsCollapsed);
			}
		}
		
		container.appendChild(chapterElement);
		
		Event.sinkEvents(chapterElement, Event.ONCLICK);
		Event.setEventListener(chapterElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				if ($(Element.as(event.getEventTarget())).is(".expandChapterBtn")) {
					// Our event handler is assigned to container and to allow inner chapter elements
					// to catch their actual events we need to stop the propagation.
					// But if it's expand button - we need to stop handling event in GWT and let native 
					// handlers to kick off.
					return;
				}
				
				if (selectedNode != null && selectedNode == chapter) {
					return;
				}
				
				event.stopPropagation();
				selectChapter(chapter);
			}
		});
		
		elements.put(chapter, chapterElement);
		
		return addedPages;
	}
	
	public void selectChapter(IChapter chapter) {
		deselectCurrentElement();

		selectedNode = chapter;
		selectionController.setContentNode(selectedNode);
		onSelectionAction.execute();
		
		DivElement chapterElement = (DivElement) elements.get(chapter);
		chapterElement.addClassName("selected");
	}
	
	public void refreshCommons() {
		clearContainer(commons);
		
		PageList commonPages = this.content.getCommonPages();
		List<Page> allCommons = commonPages.getAllPages();
		
		for (Page page : allCommons) {
			addCommonPageElement(commons, page);
		}
	}
	
	private void addCommonPageElement(DivElement container, final Page page) {
		addPageElement(container, page, page.getName(), null, false);
	}
	
	private void addNavigationPageElement(DivElement container, final Page page, int index, boolean parentIsCollapsed) {
		addPageElement(container, page, page.getName(), index, parentIsCollapsed);
	}
	
	private void addPageElement(DivElement container, final Page page, String title, Integer index, boolean parentIsCollapsed) {
		
		final AnchorElement listItem = Document.get().createAnchorElement();
		listItem.setClassName("listItem");
		listItem.setInnerText(index == null ? title : "(" + index + ") " + title);
		listItem.setId(page.getId());
		
		Style style = listItem.getStyle();
		if (parentIsCollapsed == true) {
			style.setDisplay(Display.NONE);
		}
		else {
			style.setDisplay(Display.BLOCK);
		}
		
		if (page.isReportable()) {
			listItem.addClassName("reportable");
		}
		
		container.appendChild(listItem);
		
		Event.sinkEvents(listItem, Event.ONCLICK);
		Event.setEventListener(listItem, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.stopPropagation();
				
				
				deselectCurrentElement();
				selectedNode = page;
				selectionController.setContentNode(selectedNode);
				onSelectionAction.execute();

				listItem.addClassName("selected");
			}
		});
		
		elements.put(page, listItem);
		pageIndexes.put(page.getId(), index);
	}
	
	private void deselectCurrentElement() {
		if (selectedNode == null) {
			return;
		}
		
		if(elements.get(selectedNode) == null) {
			return;
		}

		elements.get(selectedNode).removeClassName("selected");
		selectedNode = null;
	}
	
	private void clearContainer (DivElement container) {
		while (container.hasChildNodes()) {
			container.removeChild(container.getLastChild());
		}
	}
	
	public IContentNode getSelectedNode() {
		return this.selectedNode;
	}
	
	public void setSelectedNode(IContentNode node) {
		deselectCurrentElement();
		selectedNode = node;
		
		Element element = this.elements.get(selectedNode);
		if (element != null) {
			element.addClassName("selected");
		}
	}

	public void refreshSelectedNode() {
		if (selectedNode instanceof Page) {
			Page selectedPage = (Page) selectedNode;
			Integer index = pageIndexes.get(selectedPage.getId());
			
			String pageTitle = selectedPage.getName();
			if (index != null) {
				pageTitle = "(" + pageIndexes.get(selectedPage.getId()) + ") " + pageTitle;
			}
			
			AnchorElement anchorElement = (AnchorElement) elements.get(selectedNode);
			anchorElement.setInnerText(pageTitle);
			if (selectedPage.isReportable()) {
				anchorElement.addClassName("reportable");
			} else {
				anchorElement.removeClassName("reportable");
			}
		} else {
			Element chapterElement = elements.get(selectedNode);
			$(chapterElement).find(".chapterName").first().html(selectedNode.getName() + "<a class=\"expandChapterBtn\"></a>");
		}
	}
	
	public void updateElementsTexts() {
		boxTitle.setInnerText(DictionaryWrapper.get("pages"));
		mainTab.setInnerText(DictionaryWrapper.get("main_tab"));
		commonsTab.setInnerText(DictionaryWrapper.get("commons_tab"));
	}
	
	private void setNavigation() {
		if ($navigation == null) {
			$navigation = $("#pagesList-navigation");
		}
	}
	
	private void setCommons() {
		if ($commons == null) {
			$commons = $("#pagesList-commons");
		}
	}

	private void hideMain() {
		setNavigation();
		$navigation.css(CSS.DISPLAY.with(Display.NONE));
	}
	
	private void hideCommons() {
		setCommons();
		$commons.css(CSS.DISPLAY.with(Display.NONE));
	}
	
	private void showMain() {
		setNavigation();
		$navigation.css(CSS.DISPLAY.with(Display.BLOCK));
	}
	
	private void showCommons() {
		setCommons();
		$commons.css(CSS.DISPLAY.with(Display.BLOCK));
	}


	
	private void connectHandlers() {
		Event.sinkEvents(mainTab, Event.ONCLICK);
		Event.setEventListener(mainTab, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.stopPropagation();
				
				if (mainTab.getClassName().contains(TAB_ACTIVE_CSS_CLASS)) {
					deselectCurrentElement();
					
					selectionController.setContentNode(null);
				}
				
				commonsTab.removeClassName(TAB_ACTIVE_CSS_CLASS);
				mainTab.addClassName(TAB_ACTIVE_CSS_CLASS);

				hideCommons();
				showMain();
			}
		});

		Event.sinkEvents(commonsTab, Event.ONCLICK);
		Event.setEventListener(commonsTab, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.stopPropagation();
				
				mainTab.removeClassName(TAB_ACTIVE_CSS_CLASS);
				commonsTab.addClassName(TAB_ACTIVE_CSS_CLASS);

				hideMain();
				showCommons();
			}
		});	
	}
	
	
	private void setPanelsID() {
		main.setId(MAIN_ID);
		commons.setId(COMMONS_ID);
	}
}

class ElementIterator implements Iterable<Element> {

    public ElementIterator(Node parent) {
        child = parent.getFirstChild();
    }
    
    private Node child;

    @Override
    public Iterator<Element> iterator() {
        Iterator<Element> it = new Iterator<Element>() {

        	Element nextElem;
        	
            @Override
            public boolean hasNext() {
            	return getNext();
            }
            
            public boolean getNext() {
            	nextElem = null;
            	
            	while (child != null)
            	{
        			if (child.getNodeType() == Node.ELEMENT_NODE) {
        				Element elem = (Element) child;
        		
        				if ( PagesWidget.elementHasClassName(elem, "ps-scrollbar-x-rail") || PagesWidget.elementHasClassName(elem, "ps-scrollbar-y-rail") )	{
        					child = child.getNextSibling();
        					continue;
        				}
        				nextElem = elem;
        				child = child.getNextSibling();
        				return true;
        			}
        			else {
        				child = child.getNextSibling();
        				continue;
        			}
            	} 
            	return false;
            }

            @Override
            public Element next() {
            	return nextElem;
            }

            @Override
            public void remove() {
                throw new UnsupportedOperationException();
            }
        };
        return it;
    }
}

