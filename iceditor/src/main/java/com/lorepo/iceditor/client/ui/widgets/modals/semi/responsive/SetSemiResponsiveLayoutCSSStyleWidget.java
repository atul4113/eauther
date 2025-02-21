package com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive;

import java.util.Collection;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveCSSListWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.CssStyle;

public class SetSemiResponsiveLayoutCSSStyleWidget extends Composite {

	private static SetSemiResponsiveLayoutCSSStyleWidgetUiBinder uiBinder = GWT.create(SetSemiResponsiveLayoutCSSStyleWidgetUiBinder.class);

	interface SetSemiResponsiveLayoutCSSStyleWidgetUiBinder extends UiBinder<Widget, SetSemiResponsiveLayoutCSSStyleWidget> {}

	private SetSemiResponsiveLayoutCSSStyle listener;
	
	@UiField SpanElement title;
	@UiField SemiResponsiveCSSListWidget stylesList;
	@UiField AnchorElement acceptButton;
	@UiField AnchorElement declineButton;

	public SetSemiResponsiveLayoutCSSStyleWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.updateElementsText();
		this.connectHandlers();
	}
	
	public void setCssStyles(Collection<CssStyle> styles) {
		this.stylesList.setSemiResponsiveCssStyles(styles);
	}

	public void setListener(SetSemiResponsiveLayoutCSSStyle modalListener) {
		this.listener = modalListener;
	}

	public String getStyleID() {
		return this.stylesList.getSelectedSemiResponsiveCSSStyle();
	}
	
	private void connectHandlers() {
		this.connectAcceptButtonHandler();
		this.connectDeclineButtonHandler();
	}
	
	private void connectDeclineButtonHandler() {
		Event.sinkEvents(this.declineButton, Event.ONCLICK);
		Event.setEventListener(this.declineButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK == event.getTypeInt()) {
					listener.onDecline();
				}
			}
		});
	}

	private void connectAcceptButtonHandler() {
		Event.sinkEvents(this.acceptButton, Event.ONCLICK);
		Event.setEventListener(this.acceptButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK == event.getTypeInt()) {
					String styleID = getStyleID();
					listener.onSetSemiResponsiveLayoutCSSStyle(styleID);
				}
			}
		});
	}

	private void updateElementsText() {
		this.title.setInnerHTML(DictionaryWrapper.get("set_semi_responsive_layout_css_style_title"));
		this.acceptButton.setInnerHTML(DictionaryWrapper.get("set_semi_responsive_layout_css_style_accept_action"));
		this.declineButton.setInnerHTML(DictionaryWrapper.get("set_semi_responsive_layout_css_style_decline_action"));
	}
}
