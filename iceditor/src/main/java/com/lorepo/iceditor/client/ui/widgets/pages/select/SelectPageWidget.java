package com.lorepo.iceditor.client.ui.widgets.pages.select;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.DoubleClickEvent;
import com.google.gwt.event.dom.client.DoubleClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.module.api.player.IPage;

import static com.google.gwt.query.client.GQuery.$;

public class SelectPageWidget extends Composite {
	
	private static SelectPageWidgetUiBinder uiBinder = GWT
			.create(SelectPageWidgetUiBinder.class);

	interface SelectPageWidgetUiBinder extends
			UiBinder<Widget, SelectPageWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel tab;
	@UiField AnchorElement select;

	private PageWidget selectedPageWidget = null;
	private IPage selectedPage = null;
	private boolean isSelectDisabled = false;
	private SelectPageEventListener listener = null;

	private Content template;

	public SelectPageWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("addPageFromTemplatePage");
		tab.getElement().getStyle().setDisplay(Display.BLOCK);
		hide();
		
		updateElementsTexts();
		
		connectHandlers();
	}
	
	public void setEventListener(SelectPageEventListener listener) {
		this.listener = listener;
	}
	
	private void connectHandlers() {
		Event.sinkEvents(select, Event.ONCLICK);
		Event.setEventListener(select, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				if (isSelectDisabled || selectedPageWidget == null) {
					return;
				}
				
				if (listener != null) {
					listener.onPageSelected(selectedPage);
				}
			}
		});
	}

	public void show() {
		tab.clear();
		MainPageUtils.show(panel);
		setSelectedDisabled(true);
		loadPages();
	}
	
	private void loadPages() {
		int count = template.getPageCount();
		
		for (int i = 0; i < count; i++) {
			final IPage page = template.getPage(i);

			final PageWidget pageWidget = new PageWidget();
			pageWidget.setName(page.getName());
			
			String previewURL = page.getPreview(); 
			if (previewURL == null || previewURL.isEmpty()) {
				previewURL = GWT.getModuleBaseForStaticFiles() + "theme/old/default_page.png";
			}
			pageWidget.setPreviewURL(previewURL);
			
			pageWidget.setClickHandler(new ClickHandler() {
				@Override
				public void onClick(ClickEvent event) {
					if (selectedPageWidget != null) {
						selectedPageWidget.setSelected(false);
					}
					
					pageWidget.setSelected(true);

					selectedPageWidget = pageWidget;
					selectedPage = page;

					setSelectedDisabled(false);
				}
			});
			
			pageWidget.setDoubleClickHandler(new DoubleClickHandler() {
				@Override
				public void onDoubleClick(DoubleClickEvent event) {
					listener.onPageSelected(page);
				}
			});
			
			tab.add(pageWidget);
		}
	}

	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}
	
	public void setSelectedDisabled(boolean isDisabled) {
		isSelectDisabled = isDisabled;

		if (isDisabled) {
			select.setAttribute("disabled", "disabled");
			select.getStyle().setOpacity(0.5);
		} else {
			select.removeAttribute("disabled");
			select.getStyle().setOpacity(1);
		}
	}

	public void setTemplate(Content template) {
		this.template = template;
	}
	
	public void updateElementsTexts() {
		$(panel.getElement()).find(".mainPageHeader h3").text(DictionaryWrapper.get("select_page"));
		select.setInnerText(DictionaryWrapper.get("add_page_menu"));
	}
}
