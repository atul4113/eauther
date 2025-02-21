package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;

public class SetAsDefaultCSSStyleAction extends AbstractAction {
	
	public SetAsDefaultCSSStyleAction(AppController controller) {
		super(controller);
	}
	
	private String cssStyleID;
	
	public void setStyleID(String cssStyleID) {
		this.cssStyleID = cssStyleID;
	}
	
	@Override
	public void execute() {
		try {
			Content model = this.getModel();
			model.setDefaultCSSStyle(this.cssStyleID);
			this.refreshWidgets();
			getNotifications().addMessage(DictionaryWrapper.get("semi_responsive_set_as_default_success"), NotificationType.notice, false);	
		} catch (Exception e) {
			getNotifications().addMessage(DictionaryWrapper.get("semi_responsive_set_as_default_failure"), NotificationType.error, true);
		}
	}

	private void refreshWidgets() {
		ActionFactory af = this.getActionFactory();
		AbstractAction refresh = af.getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets);
		refresh.execute();
	}
}
