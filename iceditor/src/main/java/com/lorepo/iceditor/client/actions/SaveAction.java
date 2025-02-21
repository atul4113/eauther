package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;

public class SaveAction extends AbstractAction{

	public SaveAction(IActionService service) {
		super(service);
	}

	@Override
	public void execute() {
		getServices().getAppController().saveCurrentPageAndContent();
	}
}
