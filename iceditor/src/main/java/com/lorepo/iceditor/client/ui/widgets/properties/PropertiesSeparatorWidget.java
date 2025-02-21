package com.lorepo.iceditor.client.ui.widgets.properties;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class PropertiesSeparatorWidget extends Composite {

	private static PropertiesSeparatorWidgetUiBinder uiBinder = GWT
			.create(PropertiesSeparatorWidgetUiBinder.class);

	interface PropertiesSeparatorWidgetUiBinder extends
			UiBinder<Widget, PropertiesSeparatorWidget> {
	}

	public PropertiesSeparatorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

}
