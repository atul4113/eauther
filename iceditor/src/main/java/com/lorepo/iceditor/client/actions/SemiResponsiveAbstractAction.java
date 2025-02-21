package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;

public abstract class SemiResponsiveAbstractAction extends AbstractAction {

	public SemiResponsiveAbstractAction(AppController controller) {
		super(controller);
	}
	
	protected void markAsVisited(String newLayoutID) {
		MarkLayoutAsVisitedAction action = (MarkLayoutAsVisitedAction) this.getAction(ActionType.markAsVisited);
		action.setSemiResponsiveLayoutID(newLayoutID);
		action.execute();
	}

	protected void refreshSemiResponsiveEditingWidgets() {
		this.getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets).execute();
	}
	
	protected void syncCurrentSemiResponsiveLayouts() {
		this.getAction(ActionType.syncCurrentPageSemiResponsiveLayouts).execute();
	}
	
	protected void setDefaultSemiResponsiveLayoutAsCurrent() {
		Content model = this.getModel();
		String defaultID = model.getDefaultSemiResponsiveLayoutID();
		
		ChangeCurrentContentSemiResponsiveLayoutAction action = (ChangeCurrentContentSemiResponsiveLayoutAction) this.getAction(ActionType.changeCurrentContentSemiResponsiveLayout);
		action.setNewLayoutID(defaultID);
		action.execute();
	}
	
	protected void refreshCurrentCssStyleOnly() {
		Content content = this.getModel();
		
		AppController appController = this.getAppController();
		appController.refreshStylesOnly(content.getActualStyle());
	}
	
	private AbstractAction getAction(ActionType type) {
		return this.getActionFactory().getAction(type);
	}
}
