package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import java.util.Collection;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.DeleteCSSStyleAction;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.SetAsDefaultCSSStyleAction;
import com.lorepo.iceditor.client.actions.ShowNotificationAction;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.CssStyle;

public class SemiResponsiveCSSStylesEditingFormWidget extends Composite {

	private static SemiResponsiveCSSStylesEditingFormWidgetUiBinder uiBinder = GWT.create(SemiResponsiveCSSStylesEditingFormWidgetUiBinder.class);

	interface SemiResponsiveCSSStylesEditingFormWidgetUiBinder extends UiBinder<Widget, SemiResponsiveCSSStylesEditingFormWidget> {}

	@UiField SemiResponsiveCSSListWidget semiResponsiveCSSListWidget;
	@UiField AnchorElement addSemiResponsiveCSSStyle;
	@UiField AnchorElement deleteSemiResponsiveCSSStyle;
	@UiField AnchorElement setAsDefaultSemiResponsiveCSSStyle;
	
	private AbstractAction onAddSemiResponsiveCSSStyle;
	private DeleteCSSStyleAction onDeleteSemiResponsiveCssStyle;
	private SetAsDefaultCSSStyleAction onSetAsDefaultSemiResponsiveCSSStyle;
	private ShowNotificationAction onShowNotification;
	

	public SemiResponsiveCSSStylesEditingFormWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.connectHandlers();
	}
	
	public void setCssStyles(Collection<CssStyle> styles) {
		this.semiResponsiveCSSListWidget.setSemiResponsiveCssStyles(styles);
	}

	public void setActionFactory(ActionFactory actionFactory) {
		this.onAddSemiResponsiveCSSStyle = actionFactory.getAction(ActionType.addNewCssStyle);
		this.onDeleteSemiResponsiveCssStyle = (DeleteCSSStyleAction) actionFactory.getAction(ActionType.deleteCssStyle);
		this.onSetAsDefaultSemiResponsiveCSSStyle = (SetAsDefaultCSSStyleAction) actionFactory.getAction(ActionType.setAsDefaultCSSStyle);
		this.onShowNotification = (ShowNotificationAction) actionFactory.getAction(ActionType.showNotification);
	}

	private void connectHandlers() {
		this.connectAddSemiResponsiveButtonHandler();
		this.connectDeleteSemiResponsiveButtonHandler();
		this.connectSetAsDefaultSemiResponsiveButtonHandler();
	}

	private void connectSetAsDefaultSemiResponsiveButtonHandler() {
		this.connectEventHandler(this.setAsDefaultSemiResponsiveCSSStyle, Event.ONCLICK, new EventListener() {

			@Override
			public void onBrowserEvent(Event event) {
				try {
					if (Event.ONCLICK == event.getTypeInt()) {
						String styleID = getSelectedSemiResponsiveCSSStyle();
						onSetAsDefaultSemiResponsiveCSSStyle.setStyleID(styleID);
						onSetAsDefaultSemiResponsiveCSSStyle.execute();
					}	
				} catch (IllegalArgumentException e) {
					showWarningNotification(e);
				}
			}
		});
	}

	private void showWarningNotification(IllegalArgumentException e) {
		this.onShowNotification.setText(e.getMessage());
		this.onShowNotification.setType(NotificationType.warning);
		this.onShowNotification.setIsClosable(false);
		this.onShowNotification.execute();
	}

	private void connectDeleteSemiResponsiveButtonHandler() {
		this.connectEventHandler(this.deleteSemiResponsiveCSSStyle, Event.ONCLICK, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK == event.getTypeInt()) {
					try {
						String styleID = getSelectedSemiResponsiveCSSStyle();
						onDeleteSemiResponsiveCssStyle.setStyleToDelete(styleID);
						onDeleteSemiResponsiveCssStyle.execute();	
					} catch (IllegalArgumentException e) {
						showWarningNotification(e);
					}
				}
			}
		});		
	}
	
	private String getSelectedSemiResponsiveCSSStyle() {
		String layoutID = this.semiResponsiveCSSListWidget.getSelectedSemiResponsiveCSSStyle();
		if (layoutID == null) {
			throw new IllegalArgumentException(DictionaryWrapper.get("semi_responsive_layout_panel_select_css_style_first"));
		}
		return layoutID;
	}

	private void connectAddSemiResponsiveButtonHandler() {
		this.connectEventHandler(this.addSemiResponsiveCSSStyle, Event.ONCLICK, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK == event.getTypeInt()) {
					onAddSemiResponsiveCSSStyle.execute();
				}
			}
		});
	}

	private void connectEventHandler(Element element, int eventbits, EventListener eventListener) {
		Event.sinkEvents(element, eventbits);
		Event.setEventListener(element, eventListener);
	}
}
