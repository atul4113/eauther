package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class ListItemTitleWidget extends Composite {

	private static ListItemTitleWidgetUiBinder uiBinder = GWT
			.create(ListItemTitleWidgetUiBinder.class);

	interface ListItemTitleWidgetUiBinder extends
			UiBinder<Widget, ListItemTitleWidget> {
	}
	
	@UiField HTMLPanel panel;

	public ListItemTitleWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Title span").html(name);		
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public com.google.gwt.dom.client.Element getArrowUpElement() {
		return $(getRootElement()).find(".propertiesItem-MoveUp").get(0);
	}
	
	public com.google.gwt.dom.client.Element getArrowDownElement() {
		return $(getRootElement()).find(".propertiesItem-MoveDown").get(0);
	}
	
	public com.google.gwt.dom.client.Element getRemoveElement() {
		return $(getRootElement()).find(".propertiesItem-DeleteBtn").get(0);
	}
}
