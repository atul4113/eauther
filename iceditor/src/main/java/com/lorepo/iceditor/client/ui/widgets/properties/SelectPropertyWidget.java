package com.lorepo.iceditor.client.ui.widgets.properties;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Node;
import com.google.gwt.dom.client.NodeList;
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

public class SelectPropertyWidget extends Composite {

	private static SelectPropertyWidgetUiBinder uiBinder = GWT
			.create(SelectPropertyWidgetUiBinder.class);

	interface SelectPropertyWidgetUiBinder extends
			UiBinder<Widget, SelectPropertyWidget> {
	}
	
	@UiField HTMLPanel panel;

	public SelectPropertyWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public void setName(String name) {
		$(getRootElement()).find(".propertyLabel").html(name);		
	}
	
	public void setValue(String[] options, String selectedOption) {
		Element selectElement = getSelectElement();
		
		for (String key : options) {
			OptionElement option = Document.get().createOptionElement();
			option.setValue(key);
			option.setText(key);
			
			option.setSelected(selectedOption.equals(key));
			
			selectElement.appendChild(option);
		}
	}

	public void setText(String[] text) {
		Element selectElement = this.getSelectElement();
		
		NodeList<Node> nodes = selectElement.getChildNodes();
		
		for (int i = 0; i < nodes.getLength() && i < text.length; i++) {
			Node node = nodes.getItem(i);
			if (node.getNodeType() == Node.ELEMENT_NODE) {
				Element option = (Element) node;
				option.setInnerText(text[i]);
			}
		}
	}
	
	private GQuery getSelectQueryElement() {
		return $(getRootElement()).find(".propertyValue select");
	}
	
	private Element getSelectElement() {
		return (Element) getSelectQueryElement().get(0);
	}

	private Element getRootElement() {
		return panel.getElement();
	}

	public void setListener(final SelectPropertyChangeListener listener) {
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
}
