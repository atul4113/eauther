package com.lorepo.iceditor.client.ui.widgets.content;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.LabelElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorEventListener;

public class LayoutWidget extends Composite {

	private static LayoutWidgetUiBinder uiBinder = GWT
			.create(LayoutWidgetUiBinder.class);

	interface LayoutWidgetUiBinder extends
			UiBinder<Widget, LayoutWidget> {
	}
	
	public LayoutWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	@UiField HTMLPanel panel;
	@UiField InputElement leftLabel;
	@UiField InputElement rightLabel;
	@UiField LabelElement useLeft;
	@UiField LabelElement useRight;
	@UiField LabelElement useLabel;
	@UiField HeadingElement title;
	public void setListener(FileSelectorEventListener fileSelectorEventListener) {
				
	}
}
