package com.lorepo.iceditor.client.semi.responsive.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.DeleteSemiResponsiveLayoutAction;
import com.lorepo.iceditor.client.actions.SetAsDefaultSemiResponsiveLayout;
import com.lorepo.iceditor.client.actions.SetSemiResponsiveLayoutStyleAction;
import com.lorepo.iceditor.client.actions.ShowNotificationAction;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class SemiResponsiveLayoutsActionButtonsWidget extends Composite {

	private static SemiResponsiveLayoutsActionButtonsWidgetUiBinder uiBinder = GWT.create(SemiResponsiveLayoutsActionButtonsWidgetUiBinder.class);

	interface SemiResponsiveLayoutsActionButtonsWidgetUiBinder extends
			UiBinder<Widget, SemiResponsiveLayoutsActionButtonsWidget> {
	}
	
	@UiField AnchorElement addSemiResponsiveLayout;
	@UiField AnchorElement deleteSemiResponsiveLayout;
	@UiField AnchorElement setAsDefaultSemiResponsiveLayout;
	@UiField AnchorElement setSemiResponsiveLayoutCssStyle;
	
	private AbstractAction onAddSemiResponsiveLayout;
	private DeleteSemiResponsiveLayoutAction onDeleteSemiResponsiveLayout;
	private SetAsDefaultSemiResponsiveLayout onSetAsDefaultSemiResponsiveLayout;
	private SetSemiResponsiveLayoutStyleAction onSetSemiResponsiveLayoutCssStyle;
	private ShowNotificationAction onShowNotification;
	
	public GetSelectedSemiResponsiveLayout getSelectedSemiResponsiveLayout = new GetSelectedSemiResponsiveLayout() {
		@Override
		public String getValue() {
			throw new IllegalArgumentException(DictionaryWrapper.get("semi_responsive_layout_panel_select_layout_first"));
		}
	};

	public SemiResponsiveLayoutsActionButtonsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		this.connectHandlers();
	}
	
	public void setGetSelectedSemiResponsiveLayout(GetSelectedSemiResponsiveLayout handler) {
		this.getSelectedSemiResponsiveLayout = handler;
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		this.onAddSemiResponsiveLayout = actionFactory.getAction(ActionType.addSemiResponsiveLayout);
		this.onDeleteSemiResponsiveLayout = (DeleteSemiResponsiveLayoutAction) actionFactory.getAction(ActionType.deleteSemiResponsiveLayout);
		this.onSetAsDefaultSemiResponsiveLayout = (SetAsDefaultSemiResponsiveLayout) actionFactory.getAction(ActionType.setAsDefaultSemiResponsiveLayout);
		this.onSetSemiResponsiveLayoutCssStyle = (SetSemiResponsiveLayoutStyleAction) actionFactory.getAction(ActionType.setSemiResponsiveLayoutStyle);
		this.onShowNotification = (ShowNotificationAction) actionFactory.getAction(ActionType.showNotification);
	}
	
	public void setHideCSSButton(boolean shouldHide) {
		if (shouldHide) {
			this.setSemiResponsiveLayoutCssStyle.getStyle().setDisplay(Display.NONE);
		}
	}
	
	private void connectHandlers() {
		this.connectAddSemiResponsiveButtonHandler();
		this.connectDeleteSemiResponsiveButtonHandler();
		this.connectSetAsDefaultSemiResponsiveButtonHandler();
		this.connectSetSemiResponsiveStyleButtonHandler();
	}
	
	private void connectAddSemiResponsiveButtonHandler() {
		EventListener listener = new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK == event.getTypeInt()) {
					onAddSemiResponsiveLayout.execute();
				}
			}
		};
		this.connectEventHandler(this.addSemiResponsiveLayout, Event.ONCLICK, listener);
	}
	
	private void connectSetSemiResponsiveStyleButtonHandler() {
		EventListener listener = new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				try {
					if (Event.ONCLICK == event.getTypeInt()) {
						onSetSemiResponsiveLayoutCssStyle.setSemiResponsiveLayoutID(getSelectedSemiResponsiveLayout.getValue());
						onSetSemiResponsiveLayoutCssStyle.execute();
					}	
				} catch (IllegalArgumentException e) {
					showWarningMessage(e);
				}
			}
		};
		
		this.connectEventHandler(this.setSemiResponsiveLayoutCssStyle, Event.ONCLICK, listener);
	}

	private void connectSetAsDefaultSemiResponsiveButtonHandler() {
		EventListener listener = new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				try {
					if (Event.ONCLICK == event.getTypeInt()) {
						onSetAsDefaultSemiResponsiveLayout.setDefaultLayoutID(getSelectedSemiResponsiveLayout.getValue());
						onSetAsDefaultSemiResponsiveLayout.execute();
					}	
				} catch (IllegalArgumentException e) {
					showWarningMessage(e);
				}
			}
		};
		this.connectEventHandler(this.setAsDefaultSemiResponsiveLayout, Event.ONCLICK, listener);
	}

	private void connectDeleteSemiResponsiveButtonHandler() {
		EventListener listener = new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				try {
					if (Event.ONCLICK == event.getTypeInt()) {
						onDeleteSemiResponsiveLayout.setPageLayoutID(getSelectedSemiResponsiveLayout.getValue());
						onDeleteSemiResponsiveLayout.execute();
					}	
				} catch (IllegalArgumentException e) {
					showWarningMessage(e);
				}
			}
		};
		this.connectEventHandler(this.deleteSemiResponsiveLayout, Event.ONCLICK, listener);
	}
	
	private void connectEventHandler(Element element, int eventBits, EventListener listener) {
		Event.sinkEvents(element, eventBits);
		Event.setEventListener(element, listener);
	}

	private void showWarningMessage(IllegalArgumentException e) {
		this.onShowNotification.setText(e.getMessage());
		this.onShowNotification.setType(NotificationType.warning);
		this.onShowNotification.setIsClosable(false);
		this.onShowNotification.execute();
	}
}
