package com.lorepo.iceditor.client.actions;

import java.util.Collection;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.layout.PageLayout;


public class ListAvailableLayoutsAction extends AbstractAction {
	
	public ListAvailableLayoutsAction(AppController controller) {
		super(controller);
	}
	
	@Override
	public void execute() {

		Content model = getModel();
		String currentLayout = model.getActualSemiResponsiveLayoutID();

		Collection<PageLayout> layouts = model.getActualSemiResponsiveLayouts();
		
		for(PageLayout layout : layouts) {
			if (layout.getID().equals(currentLayout)) {
				layouts.remove(layout);
				break;
			}
		}
		
		getAppFrame().getProperties().getLayoutsCopier().setLayouts(layouts);
	}
	
}