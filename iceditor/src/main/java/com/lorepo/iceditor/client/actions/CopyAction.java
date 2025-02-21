package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.Iterator;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class CopyAction extends AbstractPageAction{

	public CopyAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}
		
		ArrayList<String> data = new ArrayList<String>();
		Iterator<IModuleModel> modules = getServices().getSelectionController().getSelectedModules();

		while (modules.hasNext()) {
			data.add(modules.next().toXML());
		}

		if (data.size() > 0) {
			getServices().getClipboard().setData(data);
		}
	}
}
