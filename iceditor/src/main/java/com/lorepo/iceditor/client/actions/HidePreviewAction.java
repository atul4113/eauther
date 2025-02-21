package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.ui.AppFrame;

public class HidePreviewAction extends AbstractAction{

	public HidePreviewAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		AppFrame appFrame = getServices().getAppController().getAppFrame();

		appFrame.hidePreview();
	}
}
