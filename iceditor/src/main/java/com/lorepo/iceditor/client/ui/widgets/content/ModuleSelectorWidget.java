package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class ModuleSelectorWidget extends Composite {

	private static ModuleSelectorWidgetUiBinder uiBinder = GWT
			.create(ModuleSelectorWidgetUiBinder.class);

	interface ModuleSelectorWidgetUiBinder extends
			UiBinder<Widget, ModuleSelectorWidget> {
	}
	
	public ModuleSelectorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public void setPixelSize(int width, int height) {
		if (width >= 0) {
			setWidth(width + "px");
		}

		if (height >= 0) {
			setHeight(height + "px");
		}
	}
}
