package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;

public class SetAsDefaultSemiResponsiveLayout extends AbstractAction {
	
	private String newDefaultLayoutID;

	public SetAsDefaultSemiResponsiveLayout(AppController controller) {
		super(controller);
	}
	
	public void setDefaultLayoutID(String defaultLayoutID) {
		this.newDefaultLayoutID = defaultLayoutID;
	}
	
	@Override
	public void execute() {
		Content model = this.getModel();
		model.setDefaultSemiResponsiveLayout(newDefaultLayoutID);
		model.setDefaultCSSStyle(newDefaultLayoutID);
		this.refreshWidgets();
	}

	private void refreshWidgets() {
		ActionFactory af = this.getActionFactory();
		AbstractAction refresh = af.getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets);
		refresh.execute();
	}
}
