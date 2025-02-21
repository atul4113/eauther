package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class MoveCommonsToNaviAction extends AbstractAction{

	public MoveCommonsToNaviAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		Content content = getServices().getModel();
		IAppController controller = getServices().getAppController(); 
		Page page = controller.getCurrentPage();
				
		if (page == null) {
			return; // Action triggered while chapter is selected
		};
		
		if (!content.getCommonPages().contains(page)) {
			return;
		}

		content.getCommonPages().remove(page);
		content.getPages().add(page);

		controller.saveContent();

		controller.getAppFrame().getPages().refresh();
		controller.getAppFrame().getPages().setSelectedNode(page);
	}
}
