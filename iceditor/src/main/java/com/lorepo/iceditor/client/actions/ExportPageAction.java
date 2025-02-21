package com.lorepo.iceditor.client.actions;

import com.google.gwt.core.client.JavaScriptObject;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.services.local.storage.LocalStorage;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class ExportPageAction extends AbstractAction{

	public ExportPageAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		Page page = appController.getCurrentPage();
		
		Content model = this.getModel();
		LocalStorage.write(page.toXML(), page.getPreview(), Boolean.toString(page.isReportable()), model.getSemiResponsiveLayoutsAsJS());

		appFrame.getNotifications().addMessage(DictionaryWrapper.get("page_exported"), NotificationType.notice, false);
	}
	
	
}
