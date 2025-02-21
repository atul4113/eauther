package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.properties.IEnumSetProperty;
import com.lorepo.icf.properties.IProperty;

public class SelectListItemWidget extends Composite implements IListItemWidget{

	private static SelectListItemWidgetUiBinder uiBinder = GWT
			.create(SelectListItemWidgetUiBinder.class);

	interface SelectListItemWidgetUiBinder extends
			UiBinder<Widget, SelectListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private IProperty property;
	private String startVal = "";
	public SelectListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Label").html(name);		
	}
	
	public void setValue(String[] options, String selectedOption) {
		Element selectElement = getSelectElement();	
		boolean selected = false;
		for (String key : options) {
			OptionElement option = Document.get().createOptionElement();
			option.setValue(key);
			option.setText(key);
			
			option.setSelected(selectedOption.equals(key));
			if (selectedOption.equals(key)) {
				selected = true;
			}
			
			selectElement.appendChild(option);
		}
		if (!selected) {
			if (options.length > 0) {
				this.getSelectQueryElement().val(options[0]);
				this.startVal = options[0];
			}
		}
	}
	
	private GQuery getSelectQueryElement() {
		return $(getRootElement()).find(".propertiesItem-Value select");
	}
	
	private Element getSelectElement() {
		return (Element) getSelectQueryElement().get(0);
	}

	private Element getRootElement() {
		return panel.getElement();
	}

	public void setListener(final SelectListItemChangeListener listener) {
		Element selectElement = getSelectElement();
		
		Event.sinkEvents(selectElement, Event.ONCHANGE);
		Event.setEventListener(selectElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCHANGE != event.getTypeInt()) {
					return;
				}
				
				if (listener != null) {
					listener.onChange(getSelectQueryElement().val());
				}
			}
		});
	}

	@Override
	public void setProperty(IProperty property) {
		this.property = property;
		IEnumSetProperty casted = (IEnumSetProperty)property;
		String[] options = new String[casted.getAllowedValueCount()];
		for (int j = 0; j < options.length; j++) {
			options[j] = casted.getAllowedValue(j);
		}

		this.setValue(options, casted.getValue());
		this.startVal = casted.getValue();
		
	}

	@Override
	public void save() {
		this.property.setValue(this.getSelectQueryElement().val());
		
	}

	@Override
	public void reset() {
		this.startVal = this.getSelectQueryElement().val();
	}

	@Override
	public boolean isModified() {
		return !this.startVal.equals(this.getSelectQueryElement().val());
	}
}
