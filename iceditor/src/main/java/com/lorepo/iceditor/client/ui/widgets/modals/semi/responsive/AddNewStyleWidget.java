package com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.CssStyle;

public class AddNewStyleWidget extends Composite {

	private static AddNewStyleWidgetUiBinder uiBinder = GWT
			.create(AddNewStyleWidgetUiBinder.class);

	interface AddNewStyleWidgetUiBinder extends
			UiBinder<Widget, AddNewStyleWidget> {
	}

	public AddNewStyleWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsTexts();
		this.connectHandlers();
	}

	@UiField AnchorElement addButton;
	@UiField AnchorElement declineButton;	
	@UiField SpanElement title;
	@UiField SpanElement textBefore;
	@UiField InputElement styleName;
	
	private AddNewStyle listener;

	public void setListener(AddNewStyle listener) {
		this.listener = listener;
	}
	
	public String getStyleName() {
		return this.styleName.getValue();
	}
	
	private void connectHandlers() {
		this.sinkEventsAddButton();
		this.sinkEventsDeclineButton();
	}

	private void sinkEventsDeclineButton() {
		Event.sinkEvents(this.declineButton, Event.ONCLICK);
		Event.setEventListener(this.declineButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				listener.onDecline();
			}
		});
	}
	
	private void sinkEventsAddButton() {
		Event.sinkEvents(this.addButton, Event.ONCLICK);
		Event.setEventListener(this.addButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				String cssStyleName = styleName.getValue();
				CssStyle justCreatedStyle = CssStyle.createNewStyle(cssStyleName);
				listener.onAddStyle(justCreatedStyle);
			}
		});
	}

	private void updateElementsTexts() {
		this.title.setInnerHTML(DictionaryWrapper.get("add_new_style_title"));
		this.textBefore.setInnerHTML(DictionaryWrapper.get("add_new_style_style_name") + ":");
		this.addButton.setInnerHTML(DictionaryWrapper.get("add_new_style_add_action"));
		this.declineButton.setInnerHTML(DictionaryWrapper.get("add_new_style_decline_action"));
	}
}
