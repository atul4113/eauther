package com.lorepo.iceditor.client.actions;

import java.util.HashMap;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.modals.semi.responsive.AddNewStyle;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;

public class AddNewCSSStyleAction extends AbstractAction {
	public AddNewCSSStyleAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {
		this.getModals().addNewStyle(new AddNewStyle() {
			
			@Override
			public void onDecline() {}
			
			@Override
			public void onAddStyle(CssStyle newCssStyle) {
				try {
					addNewStyle(newCssStyle);
					refresh();
				} catch (IllegalArgumentException e) {
					getNotifications().addMessage(e.getMessage(), NotificationType.error, true);
				}
			}
		});
	}
	
	private void addNewStyle(CssStyle newCssStyle) {
		Content contentModel = this.getModel();
		HashMap<String, CssStyle> styles = contentModel.getStyles();
		if (styles.containsKey(newCssStyle.getID())) {
			throw new IllegalArgumentException(DictionaryWrapper.get("add_new_style_error_same_id"));
		}
		
		String name = newCssStyle.getName().trim();
		if (name.compareTo("") == 0) {
			throw new IllegalArgumentException(DictionaryWrapper.get("add_new_style_error_empty_name"));
		}
		
		
		newCssStyle.setValue(contentModel.getDefaultCssStyle().getValue());
		contentModel.setStyle(newCssStyle);
	}
	
	private void refresh() {
		ActionFactory af = this.getActionFactory();
		AbstractAction action = af.getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets);
		action.execute();
	}
}
