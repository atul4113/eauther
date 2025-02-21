package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationMessageID;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class RemoveChapterAction extends AbstractAction{

	public RemoveChapterAction(IActionService service) {
		super(service);
	}
	
	private void removePageLimitExceededMessage() {
		getServices().getNotifiacatonFactory().removeMessage(NotificationMessageID.too_many_pages);		
	}
	
	@Override
	public void execute() {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		final IContentNode node = appController.getSelectionController().getSelectedContent();
		
		if (!(node instanceof IChapter)) {
			return;
		}
		
		String message = DictionaryWrapper.get("delete_chapter_confirmation") + node.getName();
		appFrame.getModals().addModal(message, new QuestionModalListener() {
			@Override
			public void onDecline() {}
			
			@Override
			public void onAccept() {
				removeChapter(node);
				if(!getModel().isPageLimitExceeded()){
					removePageLimitExceededMessage();
				}
			}
		});
		
	}

	public void refreshAndSwitchPage() {
		getServices().getAppController().getAppFrame().getPages().refresh();
		
		if (getModel().getPages().size() == 0) {
			return;
		}

		Page page = getModel().getPages().getAllPages().get(0);
		getServices().getAppController().switchToPage(page, false);
		getServices().getAppController().saveContent();
	}
	
	private void removeChapter(final IContentNode node) {
		IAppController appController = getServices().getAppController();
		AppFrame appFrame = appController.getAppFrame();
		String message = DictionaryWrapper.get("delete_chapter_pages_confirmation");
		appFrame.getModals().addModal(message, new QuestionModalListener() {
			@Override
			public void onDecline() {
				getModel().getPages().removeFromTree(node, false);
				refreshAndSwitchPage();
			}
			
			@Override
			public void onAccept() {
				getModel().getPages().removeFromTree(node, true);
				refreshAndSwitchPage();
			}
		});
	}
}
