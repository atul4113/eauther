package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class CloseEditorAction extends AbstractAction{

	public CloseEditorAction(IActionService services) {
		super(services);
	}

	
	@Override
	public void execute() {
		if(getServices().getAppController().isAllowClose()) {
			if (getServices().getAppController().isSavingStyles()) {
				getServices().getAppController().getAppFrame().getNotifications()
					.addMessage(DictionaryWrapper.get("background_saving_css"), NotificationType.notice, false);
			}
			MainPageUtils.updateWidgetScrollbars("content");
			getServices().getAppController().close();
		}
	}

}
