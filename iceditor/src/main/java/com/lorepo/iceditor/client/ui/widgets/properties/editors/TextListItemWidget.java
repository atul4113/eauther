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

public class TextListItemWidget extends Composite implements IListItemWidget {

	private static TextListItemWidgetUiBinder uiBinder = GWT
			.create(TextListItemWidgetUiBinder.class);

	interface TextListItemWidgetUiBinder extends
			UiBinder<Widget, TextListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private IProperty property;
	private String startVal = "";
	
	public TextListItemWidget() {
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
		return $(getRootElement()).find(".propertiesItem-Value textarea");
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
