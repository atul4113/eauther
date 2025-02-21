package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.icplayer.client.model.page.Page;

public class MarkLayoutAsVisitedAction extends AbstractAction {
	
	private String semiResponsiveLayoutID;
	
	public MarkLayoutAsVisitedAction(AppController controller) {
		super(controller);
	}
	
	public void setSemiResponsiveLayoutID(String layoutID) {
		this.semiResponsiveLayoutID = layoutID;
	}

	@Override
	public void execute() {
		Page page = this.getCurrentPage();
		if (page == null) {
			return;
		}
		
		String pageID = page.getId();
		SemiResponsiveModificationsHistory.markAsVisited(pageID, this.semiResponsiveLayoutID);
		SemiResponsiveModificationsHistory.setLastSeen(pageID, this.semiResponsiveLayoutID);
	}
}
