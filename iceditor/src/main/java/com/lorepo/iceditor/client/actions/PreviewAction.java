package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icplayer.client.model.page.Page;

public class PreviewAction extends AbstractAction{

	public PreviewAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		getServices().getAppController().getModyficationController().savePageIfModified(new IRequestListener() {
			@Override
			public void onFinished(String responseText) {
				MainPageUtils.triggerApplyClick();

				IAppController appController = getServices().getAppController();
				
				String previewURL = appController.getPreviewUrl();
				if (previewURL == null) {
					return;
				}

				Page page = appController.getCurrentPage();
				
				int commonPageIndex = appController.getCommonPageIndex(page.getId());
				int currentPageIndex = appController.getCurrentPageIndex();
				

				if (commonPageIndex >= 0) {
					previewURL += "#commons_" + (commonPageIndex + 1);
				} else if (currentPageIndex > 0) {
					previewURL += "#" + (currentPageIndex + 1);
				}
				
				appController.getAppFrame().showPreview(previewURL);
			}
			
			@Override
			public void onError(int reason_code) {
			}
		});
	}
}
