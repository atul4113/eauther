package com.lorepo.iceditor.client.ui.widgets.templates;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.DoubleClickEvent;
import com.google.gwt.event.dom.client.DoubleClickHandler;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.dlg.TemplatesJson;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class SelectTemplateWidget extends Composite {
	
	private static final String TEMPLATE_URL = "/editor/api/templates";

	private static SelectTemplateWidgetUiBinder uiBinder = GWT
			.create(SelectTemplateWidgetUiBinder.class);

	interface SelectTemplateWidgetUiBinder extends
			UiBinder<Widget, SelectTemplateWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel loading;
	@UiField HTMLPanel publicTab;
	@UiField HTMLPanel privateTab;
	@UiField AnchorElement publicTabButton;
	@UiField AnchorElement privateTabButton;
	@UiField AnchorElement select;
	@UiField InputElement replace;
	@UiField HeadingElement title;
	@UiField SpanElement replaceHeaderAndFooter;
	
	private TemplatesJson templates;
	private String themeURL;
	private TemplateWidget selectedTemplate = null;
	private TemplateWidget lessonTemplate = null;
	private boolean isSelectDisabled = false;
	private SelectTemplateEventListener listener = null;

	public SelectTemplateWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("selectTemplatePage");
		updateElementsTexts();
		
		hide();
		
		connectHandlers();
	}
	
	public void setThemeURL(String themeURL) {
		this.themeURL = themeURL;
	}
	
	public void setEventListener(SelectTemplateEventListener listener) {
		this.listener = listener;
	}
	
	private void connectHandlers() {
		Event.sinkEvents(publicTabButton, Event.ONCLICK);
		Event.setEventListener(publicTabButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				selectPublicTab();
			}
		});
		
		Event.sinkEvents(privateTabButton, Event.ONCLICK);
		Event.setEventListener(privateTabButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				selectPrivateTab();
			}
		});
		
		Event.sinkEvents(select, Event.ONCLICK);
		Event.setEventListener(select, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				if (isSelectDisabled || selectedTemplate == null) {
					return;
				}
				
				if (listener != null) {
					listener.onTemplateSelected(selectedTemplate.getName(), selectedTemplate.getThemeURL(), replace.isChecked());
				}
			}
		});
	}

	public void show() {
		publicTab.clear();
		privateTab.clear();
		replace.setChecked(false);

		MainPageUtils.show(panel);
		showLoading();
		setSelectedDisabled(true);
		
		loadTemplates();
	}
	
	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
		WidgetLockerController.hide();
	}
	
	private void showLoading() {
		loading.getElement().getStyle().setDisplay(Display.BLOCK);
	}
	
	private void hideLoading() {
		loading.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	private void loadTemplates() {

		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, TEMPLATE_URL);

		try {
			builder.sendRequest(null, new RequestCallback() {
				@Override
				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() == 200){
						parseJsonData(response.getText());
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
				}
			});
		} catch (RequestException e) {
		}		
	}
	
	private void parseJsonData(String text) {
		templates = TemplatesJson.parse(text);
		
		hideLoading();
		
		initTab(publicTab, "Public");
		initTab(privateTab, "Private");
		selectPublicTab();
	}

	private void initTab(HTMLPanel tab, String name) {
		int count = 0;

		for (int i = 0; i < templates.getItemCount(); i++) { 
			if (templates.getCategory(i).equalsIgnoreCase(name)) {
				final TemplateWidget template = new TemplateWidget();

				template.setName(templates.getItemName(i));
				template.setIcon(templates.getItemIcon(i));
				template.setThemeURL(templates.getThemeUrl(i));
				
				if(themeURL != null && templates.getThemeUrl(i).compareTo(themeURL) == 0) {
					lessonTemplate = template;
					selectedTemplate = template;
					template.setSelected(true);
				}
				
				template.setClickHandler(new ClickHandler() {
					@Override
					public void onClick(ClickEvent event) {
						if (selectedTemplate != null) {
							selectedTemplate.setSelected(false);
						}

						template.setSelected(true);
						selectedTemplate = template;
						
						setSelectedDisabled(selectedTemplate == lessonTemplate);
					}
				});
				
				template.setDoubleClickHandler(new DoubleClickHandler() {
					@Override
					public void onDoubleClick(DoubleClickEvent event) {
						listener.onTemplateSelected(template.getName(), template.getThemeURL(), replace.isChecked());
					}
				});
				
				tab.add(template);
				count++;
			}
		}
		
		if (count == 0) {
			tab.getElement().addClassName("empty");
			tab.getElement().setInnerText(DictionaryWrapper.get("empty_category_select_template"));
		}
	}
	
	private void selectPublicTab() {
		publicTabButton.addClassName("selected");
		privateTabButton.removeClassName("selected");
		
		publicTab.getElement().getStyle().setDisplay(Display.BLOCK);
		privateTab.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	private void selectPrivateTab() {
		publicTabButton.removeClassName("selected");
		privateTabButton.addClassName("selected");
		
		publicTab.getElement().getStyle().setDisplay(Display.NONE);
		privateTab.getElement().getStyle().setDisplay(Display.BLOCK);
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
	
	public void updateElementsTexts() {
		publicTabButton.setInnerText(DictionaryWrapper.get("public_templates"));
		privateTabButton.setInnerText(DictionaryWrapper.get("private_templates"));
		select.setInnerText(DictionaryWrapper.get("select_template_button"));
		title.setInnerText(DictionaryWrapper.get("select_template"));
		replaceHeaderAndFooter.setInnerText(DictionaryWrapper.get("replace_header_and_footer"));
	}
}
