package com.lorepo.iceditor.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class HorizontalSeparator extends Composite{

	private static HorizontalSeparatorUiBinder uiBinder = GWT
			.create(HorizontalSeparatorUiBinder.class);

	interface HorizontalSeparatorUiBinder extends
			UiBinder<Widget, HorizontalSeparator> {
	}

	public HorizontalSeparator() {
		initWidget(uiBinder.createAndBindUi(this));
	}
}
