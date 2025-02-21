package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;

public class UndoAction extends AbstractAction{

	public UndoAction(IActionService service) {
		super(service);
	}

	@Override
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}

		getServices().getAppController().getUndoManager().undo();
	}
}
