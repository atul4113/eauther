package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IChapter;

public class MoveNaviToCommonsAction extends AbstractAction{

	public MoveNaviToCommonsAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		Content content = getServices().getModel();
		IAppController controller = getServices().getAppController(); 
		Page page = controller.getCurrentPage();

		if (page == null) {
			return; // Action triggered while chapter is selected
		}
		
		IChapter parentChapter = content.getParentChapter(page);

		if (!content.getAllPages().contains(page) || content.getPageCount() <= 1) {
			return;
		}
		
		((PageList) parentChapter).remove(page);
		content.getCommonPages().add(page);
		controller.saveContent();
		controller.getAppFrame().getPages().refresh();
		controller.getAppFrame().getPages().setSelectedNode(page);
	}

}
