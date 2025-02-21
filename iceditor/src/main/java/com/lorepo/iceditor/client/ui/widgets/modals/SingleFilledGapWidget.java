package com.lorepo.iceditor.client.ui.widgets.modals;

import static com.google.gwt.query.client.GQuery.$;

import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.InputElement;
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

public class SingleFilledGapWidget extends Composite {

	private static SingleFilledGapWidgetUiBinder uiBinder = GWT
			.create(SingleFilledGapWidgetUiBinder.class);

	interface SingleFilledGapWidgetUiBinder extends UiBinder<Widget, SingleFilledGapWidget> {
	}

	@UiField HTMLPanel panel;
	@UiField SpanElement title;
	@UiField SpanElement initialTextLabel;
	@UiField InputElement initialText;
	@UiField SpanElement feedback;
	@UiField AnchorElement add;
	@UiField SpanElement answers;
	@UiField HTMLPanel items;
	
	public SingleFilledGapWidget(String mode, List<String> values) {
		initWidget(uiBinder.createAndBindUi(this));
		feedback.setId("add_gap_feedback");
		updateElementsTexts(mode);
		items.getElement().addClassName("gapItemsList");
		$(feedback).hide();
		
		if (values != null) {
			fillItems(values);
		} else {
			addNewItem();
		}
	}
	
	private void fillItems(List<String> values) {
		$(initialText).val(values.get(0));
		if (values.size() > 1) {
			for (int i = 1; i < values.size(); i++) {
				addAndFillItem(values.get(i));
			}
		}
	}
	
	private Element getRootElement() {
		return panel.getElement();
	}
	
	private void addAndFillItem(String value) {
		ItemsGapWidget item = new ItemsGapWidget();
		item.setValue(value);
		items.add(item);
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
		initialText.focus();
	}
	
	protected void setFocusOnLastElement() {
		int itemsCount = items.getWidgetCount();
		ItemsGapWidget lastItem = (ItemsGapWidget) items.getWidget(itemsCount - 1);
		
		lastItem.answer.focus();
	}
	
	private void addNewItem() {
		ItemsGapWidget item = new ItemsGapWidget();
		items.add(item);
		setFocusOnLastElement();
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
				if (!$(initialText).val().equals("")) {
					listener.onAccept();
				} else {
					$(feedback).show().delay(1000).fadeOut();
				}
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
	
	public String getDefinition() {
		String returnedValue = "\\filledGap{" + $(initialText).val();
		
		for (int i = 0; i < items.getWidgetCount(); i++) {
			returnedValue += "|" + ((ItemsGapWidget)items.getWidget(i)).getValue();
		}
		return returnedValue + "}";
	}
	
	public void updateElementsTexts(String mode) {
		$(getRootElement()).find("a.accept").text(DictionaryWrapper.get("ok").toUpperCase());
		$(getRootElement()).find("a.decline").text(DictionaryWrapper.get("cancel").toUpperCase());
		initialTextLabel.setInnerText(DictionaryWrapper.get("initial_text_filled_gap"));
		add.setInnerText("+");
		answers.setInnerText(DictionaryWrapper.get("add_gap_answers"));
		feedback.setInnerText(DictionaryWrapper.get("fill_required_field"));
		if (mode.equals("edit")) {
			title.setInnerText(DictionaryWrapper.get("edit_filled_gap"));
		} else {
			title.setInnerText(DictionaryWrapper.get("add_filled_gap"));
		}

	}

	public String getPlaceholder() {
		return $(initialText).val();
	}

	public int getAnswerSize() {
		int maxSize = 0;
		for (int i = 0; i < items.getWidgetCount(); i++) {
			if(((ItemsGapWidget)items.getWidget(i)).getValue().length() > maxSize) {
				maxSize = ((ItemsGapWidget)items.getWidget(i)).getValue().length();
			}
		}
		return maxSize;
	}
}
