package com.lorepo.iceditor.client.actions;

import com.google.gwt.user.client.Window;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationMessageID;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;

public class RemovePageAction extends AbstractAction{

	public RemovePageAction(AppController controller) {
		super(controller);
	}	
	
	private void removePageLimitExceededMessage() {
		getServices().getNotifiacatonFactory().removeMessage(NotificationMessageID.too_many_pages);		
	}
	
	@Override
	public void execute() {
		final Page page = getServices().getAppController().getCurrentPage();
		boolean isCommonPage = getServices().getModel().getCommonPages().contains(page);

		if (!isCommonPage && getServices().getModel().getPageCount() <= 1) {
			Window.alert(DictionaryWrapper.get("cant_remove_last_page"));
			return;
		}
		
		if (page == null) {
			return;
		}
		
		AppFrame appFrame = getServices().getAppController().getAppFrame();
		String message = DictionaryWrapper.get("delete_page_confirmation") + page.getName();
		appFrame.getModals().addModal(message, new QuestionModalListener() {
			@Override
			public void onDecline() {}
			
			@Override
			public void onAccept() {
				removePage(page);
				if(!getModel().isPageLimitExceeded()){
					removePageLimitExceededMessage();
				}
			}
		});
	}

	private void removePage(Page page) {
		IAppController appController = getServices().getAppController();
		Page selectPage = null;
		PageList chapter = getCurrentChapter();

		if (chapter != null) {
			SemiResponsiveModificationsHistory.removePage(page.getId());
			chapter.remove(page);
			selectPage = getModel().getPages().getAllPages().get(0);
			appController.getAppFrame().getPages().refresh();
			appController.switchToPage(selectPage, false);
			appController.saveContent();
		}
	}
}
