package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IStaticRowProperty;

public class StaticRowListItemWidget extends Composite implements IListItemWidget {

	private static StaticRowListItemWidgetUiBinder uiBinder = GWT
			.create(StaticRowListItemWidgetUiBinder.class);

	interface StaticRowListItemWidgetUiBinder extends
			UiBinder<Widget, StaticRowListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private IProperty property;
	private boolean startVal = false;

	public StaticRowListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	@Override
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Label").html(name);		
	}
	
	@Override
	public void setProperty(IProperty property) {
		this.property = property;
		IStaticRowProperty cast = (IStaticRowProperty) property;
		getInputElement().setChecked(property.getValue().equals("True"));
	}
	
	@Override
	public void save() {
		this.property.setValue(getInputElement().isChecked() ? "True" : "False");
	}

	private GQuery getInputQueryElement() {
		return $(getRootElement()).find(".propertiesItem-Value input");
	}
	
	private InputElement getInputElement() {
		return (InputElement) getInputQueryElement().get(0);
	}

	private Element getRootElement() {
		return panel.getElement();
	}

	@Override
	public boolean isModified() {
		return startVal != getInputElement().isChecked();
	}
	
	@Override
	public void reset() {
		startVal = getInputElement().isChecked();
	}
}
