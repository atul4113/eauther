package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class PageSelectedAction extends AbstractAction{
	public PageSelectedAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		
		IContentNode node = appController.getSelectionController().getSelectedContent();
		
		if (node instanceof Page) {
			appController.switchToPage((Page) node, true);
		} else {
			appController.switchToChapter((IChapter) node);
		}
	}
}
