package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.FocusHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.Widget;

public class HTMLListItemValueWidget extends Composite {

	private static HTMLListItemWidgetUiBinder uiBinder = GWT
			.create(HTMLListItemWidgetUiBinder.class);

	interface HTMLListItemWidgetUiBinder extends
			UiBinder<Widget, HTMLListItemValueWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private RichTextArea textArea;
	private RichTextToolbar toolbar;
	private String startVal = "";

	public HTMLListItemValueWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		textArea = new RichTextArea();
		textArea.getElement().addClassName("richTextEditArea");
		
		panel.add(textArea);
		
		connectHandlers();
	}

	private void connectHandlers() {
		textArea.addFocusHandler(new FocusHandler() {
			@Override
			public void onFocus(FocusEvent event) {
				if (toolbar != null) {
					toolbar.setRichTextWidget(textArea);
				}
			}
		});
	}
	
	public boolean isModified() {
		return !startVal.equals(textArea.getText());
	}
	
	public void reset() {
		startVal = textArea.getText();
	}

	public void setToolbar(RichTextToolbar toolbar) {
		this.toolbar = toolbar;
	}
	
	public void setHTML(String html) {
		textArea.setHTML(html);
	}
	
	public void setIndex(int index) {
		textArea.setTabIndex(index);
	}

	public String getHTML() {
		toolbar.fixIndentIssue();
		return textArea.getHTML();
	}
}
