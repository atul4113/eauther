package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class PageLoadingWidget extends Composite {

	private static PresentationLoadingWidgetUiBinder uiBinder = GWT
			.create(PresentationLoadingWidgetUiBinder.class);

	interface PresentationLoadingWidgetUiBinder extends
			UiBinder<Widget, PageLoadingWidget> {
	}
	
	@UiField HTMLPanel panel;

	public PageLoadingWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("pageLoadingPage");
	}

	public void show() {
		panel.getElement().getStyle().setDisplay(Display.BLOCK);
	}
	
	public void hide() {
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}
}
