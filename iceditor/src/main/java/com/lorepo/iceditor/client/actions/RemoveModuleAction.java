package com.lorepo.iceditor.client.actions;

import java.util.Iterator;

import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class RemoveModuleAction extends AbstractPageAction {
	private boolean isModalVisible = false;
	
	public RemoveModuleAction(AppController controller) {
		super(controller);
	}

	@Override
	public void execute() {
		final IAppController appController = getServices().getAppController();
		final AppFrame appFrame = appController.getAppFrame();
		final Iterator<IModuleModel> selection = getServices().getSelectionController().getSelectedModules();
		
		if (selection == null || !selection.hasNext()) {
			return;
		}
		
		if (WidgetLockerController.isVisible()) {
			return;
		}
		
		if (isModalVisible) { // Only one delete action can be performed at once
			return;
		}
		
		isModalVisible = true;
		appFrame.getModals().addModal(DictionaryWrapper.get("delete_module_confirmation"), new QuestionModalListener() {
			@Override
			public void onDecline() {
				isModalVisible = false;
			}
			
			@Override
			public void onAccept() {
				Page page = (Page) appController.getSelectionController().getSelectedContent();

				while (selection.hasNext()) {
					IModuleModel module = selection.next();
					page.removeModule(module);
				}

				appController.getSelectionController().clearSelectedModules();

				appFrame.getPresentation().onPageSelected();
				appFrame.getModules().setPage(page);
				appFrame.getProperties().setPage(page);
				appFrame.getStyles().setPage(page);

				MainPageUtils.executeOnPageSelection();
				
				appController.saveCurrentPageAndContent();
				appController.getUndoManager().add(page.toXML());
				isModalVisible = false;
				appFrame.getPresentation().refreshView();
			}
		});
	}
}
