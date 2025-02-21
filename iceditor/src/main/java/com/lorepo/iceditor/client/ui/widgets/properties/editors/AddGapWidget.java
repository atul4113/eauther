package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.dom.client.SelectElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class AddGapWidget extends Composite {

	private static AddGapWidgetUiBinder uiBinder = GWT
			.create(AddGapWidgetUiBinder.class);

	interface AddGapWidgetUiBinder extends UiBinder<Widget, AddGapWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField SelectElement addGapOption;
	@UiField SpanElement addGapLabel;
	@UiField InputElement renderedOption;
	@UiField SpanElement renderedLabel;
	@UiField SpanElement addAltTextLabel;
	@UiField AnchorElement addAltText;
	private OptionElement selectOption = Document.get().createOptionElement();

	private enum Gap{
		editable, dropdown, filled
	}
	
	public AddGapWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		panel.getElement().setId("gapPreferences");
		addGapOption.setId("addGapOption");

		selectOption.setText("Select");
		selectOption.setAttribute("selected", "selected");
		selectOption.setAttribute("disabled", "disabled");
		addGapOption.add(selectOption, null);

		for (Gap gap : Gap.values()) {
			OptionElement option = Document.get().createOptionElement();
			option.setText(DictionaryWrapper.get(gap.name()));
			option.setValue(gap.name());
			
			addGapOption.add(option, null);
		}
		
		addGapLabel.setId("addGapLabel");
		updateElementsText();
	}
	
	public void updateElementsText() {
		addGapLabel.setInnerText(DictionaryWrapper.get("add_gap"));
		renderedLabel.setInnerText(DictionaryWrapper.get("rendered_view"));
		addAltTextLabel.setInnerText(DictionaryWrapper.get("add_alt_text_label"));
		addAltText.setInnerText("+");
	}
	
	public boolean isChecked() {
		return this.renderedOption.isChecked();
	}
	
	public void changeRenderOption(){
		this.renderedOption.click();
	}
}