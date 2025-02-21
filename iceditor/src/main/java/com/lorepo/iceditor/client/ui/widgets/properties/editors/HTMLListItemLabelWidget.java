package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class HTMLListItemLabelWidget extends Composite {

	private static HTMLListItemLabelWidgetUiBinder uiBinder = GWT
			.create(HTMLListItemLabelWidgetUiBinder.class);

	interface HTMLListItemLabelWidgetUiBinder extends
			UiBinder<Widget, HTMLListItemLabelWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	public HTMLListItemLabelWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public void setName(String name) {
		panel.getElement().setInnerText(name);		
	}
}
