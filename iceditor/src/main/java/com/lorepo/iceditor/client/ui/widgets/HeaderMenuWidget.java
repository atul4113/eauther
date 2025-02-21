package com.lorepo.iceditor.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.ui.widgets.utils.ActionUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class HeaderMenuWidget extends Composite {

	private static HeaderMenuWidgetUiBinder uiBinder = GWT
			.create(HeaderMenuWidgetUiBinder.class);

	interface HeaderMenuWidgetUiBinder extends UiBinder<Widget, HeaderMenuWidget> {
	}
	
	private AbstractAction onCloseAction;
	private AbstractAction onAbandonChangesAction;
	private AbstractAction onSaveAction;
	private AbstractAction onPreviewAction;
	private AbstractAction onHidePreviewAction;
	private AbstractAction onPreviewInNewTabAction;
	private AbstractAction onSettingsAction;
	
	@UiField AnchorElement close;
	@UiField AnchorElement abandonAllChanges;
	@UiField AnchorElement closeDropDownArrow;
	@UiField AnchorElement save;
	@UiField AnchorElement preview;
	@UiField AnchorElement previewDropDownArrow;
	@UiField AnchorElement previewInNewTab;
	@UiField AnchorElement settings;
	
	public HeaderMenuWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		closeDropDownArrow.getStyle().setDisplay(Display.NONE);
		previewDropDownArrow.getStyle().setDisplay(Display.NONE);
		
		updateElementsTexts();
	}

	private void connectHandlers() {
		ActionUtils.bindButtonWithAction(close, Event.ONCLICK, onCloseAction);
		ActionUtils.bindButtonWithAction(abandonAllChanges, Event.ONCLICK, onAbandonChangesAction);
		ActionUtils.bindButtonWithAction(save, Event.ONCLICK, onSaveAction);

		ActionUtils.bindButtonWithAction(previewInNewTab, Event.ONCLICK, onPreviewInNewTabAction);
		
		Event.sinkEvents(preview, Event.ONCLICK);
		Event.setEventListener(preview, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				if (preview.getAttribute("active").isEmpty()) {
					onPreviewAction.execute();
					preview.setAttribute("active", "true");
					preview.setInnerText(DictionaryWrapper.get("page_edit"));
				} else {
					onHidePreviewAction.execute();
					preview.removeAttribute("active");
					preview.setInnerText(DictionaryWrapper.get("page_preview"));
				}
			}
		});
		
		ActionUtils.bindButtonWithAction(settings, Event.ONCLICK, onSettingsAction);
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onCloseAction = actionFactory.getAction(ActionType.closeEditor);
		onAbandonChangesAction = actionFactory.getAction(ActionType.abandonChanges);
		onSaveAction = actionFactory.getAction(ActionType.save);
		onPreviewAction = actionFactory.getAction(ActionType.showPreview);
		onHidePreviewAction = actionFactory.getAction(ActionType.hidePreview);
		onPreviewInNewTabAction = actionFactory.getAction(ActionType.showPreviewInNewTab);
		onSettingsAction = actionFactory.getAction(ActionType.preferences);
		
		connectHandlers();
	}

	public void showAbandonButton() {
		closeDropDownArrow.getStyle().setDisplay(Display.BLOCK);
	}
	
	public void showPreviewInNewTabButton() {
		previewDropDownArrow.getStyle().setDisplay(Display.BLOCK);
	}
	
	public void updateElementsTexts() {
		settings.setInnerText(DictionaryWrapper.get("settings"));
		save.setInnerText(DictionaryWrapper.get("save_menu"));
		preview.setInnerText(DictionaryWrapper.get("page_preview"));
		previewInNewTab.setInnerText(DictionaryWrapper.get("preview_in_new_tab"));
		close.setInnerText(DictionaryWrapper.get("close_menu"));
		abandonAllChanges.setInnerText(DictionaryWrapper.get("abandon_all_changes"));
	}
}
