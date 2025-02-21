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
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveOrientationDeviceSelectorWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class AddSemiResponsiveLayoutWidget extends Composite {

	private static AddSemiResponsiveLayoutWidgetUiBinder uiBinder = GWT.create(AddSemiResponsiveLayoutWidgetUiBinder.class);

	interface AddSemiResponsiveLayoutWidgetUiBinder extends UiBinder<Widget, AddSemiResponsiveLayoutWidget> {}

	public AddSemiResponsiveLayoutWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsText();
		this.connectHandlers();
	}

	@UiField AnchorElement addButton;
	@UiField AnchorElement declineButton;
	
	@UiField SpanElement title;
	@UiField SpanElement nameLabel;
	@UiField SpanElement thresholdLabel;
	
	@UiField InputElement nameInput;
	@UiField InputElement thresholdInput;
	@UiField SemiResponsiveOrientationDeviceSelectorWidget deviceOrientationWidget;
	
	private AddNewSemiResponsiveLayout listener;
	
	public void setListener(AddNewSemiResponsiveLayout modalListener) {
		this.listener = modalListener;
	}
	
	private void connectHandlers() {
		this.sinkEventsDeclineButton();
		this.sinkEventsAddButton();
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
				
				listener.onAddNewSemiResponsiveLayout(getLayoutData());
			}
		});
	}
	
	public PageLayoutData getLayoutData () {
		String name = this.nameInput.getValue().trim();
		String treshold = this.thresholdInput.getValue().trim();
		
		return new PageLayoutData(name, treshold, this.deviceOrientationWidget.getUseDeviceOrientation(), 
								  this.deviceOrientationWidget.getDeviceOrientation());
	}
	
	private void updateElementsText() {
		this.title.setInnerHTML(DictionaryWrapper.get("add_new_semi_responsive_layout_title"));
		this.addButton.setInnerHTML(DictionaryWrapper.get("add_new_semi_responsive_layout_add_action"));
		this.declineButton.setInnerHTML(DictionaryWrapper.get("add_new_semi_responsive_layout_decline_action"));
		this.nameLabel.setInnerText(DictionaryWrapper.get("add_new_semi_responsive_layout_name_label"));
		this.thresholdLabel.setInnerText(DictionaryWrapper.get("add_new_semi_responsive_layout_threshold_label"));
	}
}
