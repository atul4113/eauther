package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JsArrayString;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class SingleGapWidget extends Composite {

	private static SingleGapWidgetUiBinder uiBinder = GWT
			.create(SingleGapWidgetUiBinder.class);

	interface SingleGapWidgetUiBinder extends UiBinder<Widget, SingleGapWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField HTMLPanel items;
	@UiField SpanElement title;
	@UiField AnchorElement add;
	@UiField SpanElement answers;
		
	public SingleGapWidget(String mode, List<String> values) {
		initWidget(uiBinder.createAndBindUi(this));
		
		items.getElement().addClassName("gapItemsList");
		updateElementsTexts(mode);
		
		if (values != null) {
			fillItems(values);
		} else {
			addNewItem();
		}
	}
	
	private void fillItems(List<String> values) {
		for (String value : values) {
			addAndFillItem(value);
		}
	}

	private void addAndFillItem(String value) {
		ItemsGapWidget item = new ItemsGapWidget();
		item.setValue(value);
		items.add(item);
	}
	
	public native void addSortableItems() /*-{
		$wnd.$('.gapItemsList').sortable({ axis: 'y', handle: ".sortable_image" });
	}-*/;
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	private com.google.gwt.dom.client.Element getAcceptElement() {
		return $(getRootElement()).find(".accept").get(0);
	}
	
	private com.google.gwt.dom.client.Element getDeclineElement() {
		return $(getRootElement()).find(".decline").get(0);
	}
	
	public void setMessage(String message) {
		$(getRootElement()).find("span").get(0).setInnerText(message);
	}
	
	protected void setFocus() {
		int itemsCount = items.getWidgetCount();
		ItemsGapWidget lastItem = (ItemsGapWidget) items.getWidget(itemsCount - 1);
		
		lastItem.answer.focus();
	}
	
	private void addNewItem() {
		ItemsGapWidget item = new ItemsGapWidget();
		items.add(item);
		setFocus();
	}
	
	public void setListener(final QuestionModalListener listener) {
		if (listener == null) {
			return;
		}
		
		com.google.gwt.dom.client.Element acceptElement = getAcceptElement();
		Event.sinkEvents(acceptElement, Event.ONCLICK);
		Event.setEventListener(acceptElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				listener.onAccept();
			}
		});
		
		com.google.gwt.dom.client.Element declineElement = getDeclineElement();
		Event.sinkEvents(declineElement, Event.ONCLICK);
		Event.setEventListener(declineElement, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();
				
				listener.onDecline();
			}
		});
		
		Event.sinkEvents(add, Event.ONCLICK);
		Event.setEventListener(add, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				event.preventDefault();
				event.stopPropagation();

				addNewItem();
				
				MainPageUtils.updateScrollBar("gapItemsList");
			}
		});
	}
	
	public native String getDefinition() /*-{
		var syntax = "",
			$_ = $wnd.$,
			$_items = $_('.gapItemsList').find('.add_gap_item');
		
		$_.each($_items, function(i, el) {
			var value = $_(el).find('input:text')[0].value;
						
			if (value !== "") {
				syntax += value + "|";
			}
		});
		
		return "\\gap{" + syntax.substring(0, syntax.length - 1) + "}";
	}-*/;
	
	public void updateElementsTexts(String mode) {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("ok").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("cancel").toUpperCase());
		add.setInnerText("+");
		answers.setInnerText(DictionaryWrapper.get("add_gap_answers"));
		
		if (mode.equals("edit")) {
			title.setInnerText(DictionaryWrapper.get("edit_editable_gap"));
		} else {
			title.setInnerText(DictionaryWrapper.get("add_editable_gap"));
		}
	}

	public native JsArrayString getValues() /*-{
		var $_ = $wnd.$,
			$_items = $_('.gapItemsList').find('.add_gap_item'),
			values = [];
		
		$_.each($_items, function(i, el) {
			var value = $_(el).find('input:text')[0].value;
						
			if (value !== "") {
				values.push(value);
			}
		});
		
		return values;
	}-*/;
}
