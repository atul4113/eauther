package com.lorepo.iceditor.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class AssetsWidget extends Composite {

	private static AssetsWidgetUiBinder uiBinder = GWT
			.create(AssetsWidgetUiBinder.class);

	interface AssetsWidgetUiBinder extends UiBinder<Widget, AssetsWidget> {
	}

	public AssetsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

}
