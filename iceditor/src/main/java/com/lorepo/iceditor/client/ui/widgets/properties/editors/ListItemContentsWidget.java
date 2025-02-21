package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class ListItemContentsWidget extends Composite {

	private static ListItemContentsWidgetUiBinder uiBinder = GWT
			.create(ListItemContentsWidgetUiBinder.class);

	interface ListItemContentsWidgetUiBinder extends
			UiBinder<Widget, ListItemContentsWidget> {
	}
	
	@UiField HTMLPanel panel;

	public ListItemContentsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public void add(Composite widget) {
		panel.add(widget);
	}
}
