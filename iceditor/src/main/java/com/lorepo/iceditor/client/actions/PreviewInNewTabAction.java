package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class PreviewInNewTabAction extends AbstractAction{
	public PreviewInNewTabAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		getServices().getAppController().getModyficationController().savePageIfModified(new IRequestListener() {
			@Override
			public void onFinished(String responseText) {
				MainPageUtils.triggerApplyClick();

				getServices().getAppController().previewInNewTab();
			}
			
			@Override
			public void onError(int reason_code) {
			}
		});
	}
}
