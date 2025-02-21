package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;

public class ModalOpenedAction extends AbstractAction{

	
	public ModalOpenedAction(AppController controller) {
		super(controller);
	}

	public void execute(String message, QuestionModalListener listener) {
		getModals().addModal(message, listener);
	}

}
