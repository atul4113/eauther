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
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class ItemsDropDownGapWidget extends Composite {

	private static ItemsGapWidgetUiBinder uiBinder = GWT
			.create(ItemsGapWidgetUiBinder.class);

	interface ItemsGapWidgetUiBinder extends UiBinder<Widget, ItemsDropDownGapWidget> {
	}

	@UiField InputElement answer;
	@UiField InputElement correct;
	@UiField HTMLPanel panel;
	@UiField AnchorElement remove;
	@UiField DivElement sortableImage;
	
	public ItemsDropDownGapWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().addClassName("add_gap_item");
		sortableImage.addClassName("sortable_image");
		answer.setAttribute("title", DictionaryWrapper.get("complete_inputs"));
		
		addHandlers();
		updateElements();
	}
	
	public boolean isCorrect() {
		return $(correct).attr("checked").equals("checked");
	}
	
	public String getAnswer() {
		return $(answer).val();
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
				boolean isCorrect = false;
				
				if (isCorrect()) {
					isCorrect = true;
				}
				if ($(".gapItemsList").find(".add_gap_item").length() > 1) {
					$(panel).remove();
					if (isCorrect) {
						resetCheckedAttribute();
					}
				}
			}
		});
		
		Event.sinkEvents(correct, Event.ONCLICK);
		Event.setEventListener(correct, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				// Simulate real radio input behaviour
				$("#modalWrapper").find("input:radio").attr("checked", false);
				$(correct).attr("checked", true);
			}
		});
	}
	private native void resetCheckedAttribute()/*-{
		$wnd.$('.gapItemsList > .add_gap_item > input[type="radio"]').each(function(i) {
			if (i==0) {
				$wnd.$(this).attr("checked","checked");
			} else {
				$wnd.$(this).removeAttr("checked");
			}
		});
	}-*/;
	public void updateElements() {
		remove.setInnerText("-");
	}
	
	public void setEnable(boolean enable) {
		$(correct).attr("checked", enable ? "" : "checked");
	}
	
	public void setValue(String value) {
		$(answer).val(value);
	}
}