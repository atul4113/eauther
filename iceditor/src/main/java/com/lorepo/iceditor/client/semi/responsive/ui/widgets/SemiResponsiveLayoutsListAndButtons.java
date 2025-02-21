package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class SemiResponsiveLayoutsListAndButtons extends Composite {

	private static SemiResponsiveLayoutsListAndButtonsUiBinder uiBinder = GWT
			.create(SemiResponsiveLayoutsListAndButtonsUiBinder.class);

	interface SemiResponsiveLayoutsListAndButtonsUiBinder extends
			UiBinder<Widget, SemiResponsiveLayoutsListAndButtons> {
	}

	public SemiResponsiveLayoutsListAndButtons() {
		initWidget(uiBinder.createAndBindUi(this));
	}
}
