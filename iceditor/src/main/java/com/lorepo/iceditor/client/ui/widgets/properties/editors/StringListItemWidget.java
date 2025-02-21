package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.properties.IProperty;

public class StringListItemWidget extends Composite implements IListItemWidget {

	private static StringListItemWidgetUiBinder uiBinder = GWT
			.create(StringListItemWidgetUiBinder.class);

	interface StringListItemWidgetUiBinder extends
			UiBinder<Widget, StringListItemWidget> {
	}
	
	@UiField HTMLPanel panel;

	private IProperty property;
	private String startVal = "";

	public StringListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	@Override
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Label").html(name);		
	}
	
	@Override
	public void setProperty(IProperty property) {
		this.property = property;
		getInputQueryElement().val(property.getValue());
	}
	
	@Override
	public void save() {
		this.property.setValue(getInputQueryElement().val());
	}
	
	private GQuery getInputQueryElement() {
		return $(getRootElement()).find(".propertiesItem-Value input");
	}

	private Element getRootElement() {
		return panel.getElement();
	}

	@Override
	public void reset() {
		startVal = getInputQueryElement().val();
	}

	@Override
	public boolean isModified() {
		return startVal != getInputQueryElement().val();
	}
}
