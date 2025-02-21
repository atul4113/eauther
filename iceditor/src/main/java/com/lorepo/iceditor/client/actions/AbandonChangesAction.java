package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.controller.Handlers;

public class AbandonChangesAction extends AbstractAction{

	public AbandonChangesAction(IActionService services) {
		super(services);
	}

	@Override
	public void execute() {
		if(getServices().getAppController().isAllowClose()) {
			getServices().removeHandler(Handlers.CloseEditorHandler);
			getServices().getAppController().abandon();
		}
	}

}
