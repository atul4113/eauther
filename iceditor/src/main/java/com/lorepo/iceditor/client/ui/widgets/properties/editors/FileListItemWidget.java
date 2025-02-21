package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.ButtonPropertyClickListener;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class FileListItemWidget extends Composite implements IListItemWidget {

	private static FileListItemWidgetUiBinder uiBinder = GWT
			.create(FileListItemWidgetUiBinder.class);

	interface FileListItemWidgetUiBinder extends
			UiBinder<Widget, FileListItemWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private IProperty property;
	private String value;
	private String startVal = "";

	public FileListItemWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		updateElementsTexts();
	}

	@Override
	public void setName(String name) {
		$(getRootElement()).find(".propertiesItem-Label").html(name);		
	}
	
	@Override
	public void setProperty(IProperty property) {
		this.property = property;
		setValue(property.getValue());
	}
	
	@Override
	public void save() {
		this.property.setValue(value);
	}
	
	public void setValue(String value) {
		this.value = value;
		
		$(getRootElement()).find(".propertiesItem-Value span").html(value);
	}
	
	public String getValue() {
		return value;
	}
	
	public void setListener(final ButtonPropertyClickListener listener) {
		final Element buttonElement = (Element) $(getRootElement()).find(".propertiesItem-Value .fileSelectButton").get(0);
		
		Event.sinkEvents(buttonElement, Event.ONCLICK);
		Event.setEventListener(buttonElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				listener.onSelected();
			}
		});
	}

	private Element getRootElement() {
		return panel.getElement();
	}
	
	public void updateElementsTexts() {
		$(panel.getElement()).find("a.fileSelectButton").text(DictionaryWrapper.get("select_file"));
		$(panel.getElement()).find(".propertiesItem-Value span").text(DictionaryWrapper.get("none"));
	}

	@Override
	public boolean isModified() {
		return !value.equals(startVal);
	}

	@Override
	public void reset() {
		startVal = value;
	}
}
