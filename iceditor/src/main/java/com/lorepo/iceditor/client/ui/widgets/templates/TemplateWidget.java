package com.lorepo.iceditor.client.ui.widgets.templates;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.DoubleClickEvent;
import com.google.gwt.event.dom.client.DoubleClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class TemplateWidget extends Composite {

	private static TemplateWidgetUiBinder uiBinder = GWT
			.create(TemplateWidgetUiBinder.class);

	interface TemplateWidgetUiBinder extends UiBinder<Widget, TemplateWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private String themeURL;
	private String templateName;

	public TemplateWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setClickHandler(ClickHandler handler) {
		panel.addDomHandler(handler, ClickEvent.getType());
	}
	
	public void setDoubleClickHandler(DoubleClickHandler handler) {
		panel.addDomHandler(handler, DoubleClickEvent.getType());
	}

	public void setName(String name) {
		this.templateName = name;

		$(getRootElement()).find(".gwt-Label").html(name);		
	}
	
	public String getName() {
		return this.templateName;
	}
	
	public void setIcon(String iconHref) {
		$(getRootElement()).find(".gwt-Image").attr("src", iconHref);
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void setSelected(boolean isSelected) {
		getRootElement().setClassName(isSelected ? "ice_template_icon-selected" : "ice_template_icon");
	}
	
	public void setThemeURL(String themeURL) {
		this.themeURL = themeURL;
	}
	
	public String getThemeURL() {
		return this.themeURL;
	}
}
