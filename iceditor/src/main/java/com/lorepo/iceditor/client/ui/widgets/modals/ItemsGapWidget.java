package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;

public class ItemsGapWidget extends Composite {

	private static ItemsGapWidgetUiBinder uiBinder = GWT
			.create(ItemsGapWidgetUiBinder.class);

	interface ItemsGapWidgetUiBinder extends UiBinder<Widget, ItemsGapWidget> {
	}

	@UiField InputElement answer;
	@UiField HTMLPanel panel;
	@UiField AnchorElement remove;
	@UiField DivElement sortableImage;
	
	public ItemsGapWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		panel.getElement().addClassName("add_gap_item");
		addHandlers();
		sortableImage.addClassName("sortable_image");
		updateElements();
	} 
	
	public String getValue() {
		return $(answer).val();
	}
	
	public void setValue(String value) {
		$(answer).val(value);
	}
	
	public void addHandlers() {
		Event.sinkEvents(remove, Event.ONCLICK);
		Event.setEventListener(remove, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				if ($(".gapItemsList").find(".add_gap_item").length() > 1) {
					$(panel).remove();
				}
			}
		});
	}
	
	public void updateElements() {
		remove.setInnerText("-");
	}
}