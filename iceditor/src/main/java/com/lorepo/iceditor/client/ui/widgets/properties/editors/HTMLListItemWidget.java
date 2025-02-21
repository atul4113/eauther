package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.utils.GapsParserUtil;
import com.lorepo.icf.properties.IProperty;

public class HTMLListItemWidget extends Composite implements IListItemWidget {

	private static HTMLListItemWidgetUiBinder uiBinder = GWT
			.create(HTMLListItemWidgetUiBinder.class);

	interface HTMLListItemWidgetUiBinder extends
			UiBinder<Widget, HTMLListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private HTMLListItemLabelWidget label;
	private HTMLListItemValueWidget value;
	private IProperty property;

	public HTMLListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		label = new HTMLListItemLabelWidget();
		value = new HTMLListItemValueWidget();
		
		panel.add(label);
		panel.add(value);
	}

	@Override
	public void setName(String name) {
		label.setName(name);
	}
	
	@Override
	public void setProperty(IProperty property) {
		this.property = property;
		value.setHTML(GapsParserUtil.renderItemsEditor(property.getValue()));
	}
	
	@Override
	public void save() {
		this.property.setValue(GapsParserUtil.unwrapGaps(value.getHTML()));
	}
	
	public void setToolbar(RichTextToolbar toolbar) {
		value.setToolbar(toolbar);
	}
	
	@Override
	public boolean isModified() {
		return value.isModified();
	}

	@Override
	public void reset() {
		value.reset();
	}
	
	protected String getValue() {
		return value.getHTML();
	}
	
	protected void setValue(String html) {
		this.value.setHTML(html);
	}
}
