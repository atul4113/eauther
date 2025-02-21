package com.lorepo.iceditor.client.actions;

import com.google.gwt.http.client.RequestException;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.IUndoManager;
import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.iceditor.client.actions.utils.ActionUtils;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;

public class AddEmptyPageAction extends AbstractAction{
	
	private int EMPTY_PAGE_HEIGHT = 450;

	public AddEmptyPageAction(IActionService service) {
		super(service);
	}
	
	@Override
	public void execute() {	
		try {
			getServices().getServerService().addPage("", new IRequestListener() {

				@Override
				public void onFinished(String pageUrl) {
					if(URLUtils.isValidUrl(pageUrl)){
						addPage(pageUrl);
						getServices().validatePageLimit();
					} else {
						getServices().showMessage(DictionaryWrapper.get("cant_add_page") + "Server returned wrong URL: \n" + pageUrl);
					}
				}

				@Override
				public void onError(int server_error) {
					getServices().getAppController().serverErrorMessage(server_error, "cant_add_page");
				}
			});

		} catch (RequestException e) {
			getServices().showMessage(e.toString());
		}

	}

	public static native int getPageHeight() /*-{
		return parseInt($wnd.$(".ic_page").css("height").replace("px",""), 10);
	}-*/;

	protected void addPage(String pageUrl) {

		IAppController appController = getServices().getAppController();
		final Page page;

		PageList chapter = getCurrentChapter();
		if(chapter != null){
			page = addPageToList(pageUrl, chapter);
			SemiResponsiveModificationsHistory.addNewPage(page.getId());

			final IRequestListener ireq = new IRequestListener() {
				private int errorCount = 0;
				private int finishedCount = 0;
				private int reason_code;

				private void updateLogic() {
					if (finishedCount + errorCount == 2) {
						if (finishedCount == 2) {
							NotificationsWidget notifications = getServices().getAppController().getAppFrame().getNotifications();
							notifications.addMessage(DictionaryWrapper.get("page_saved"), NotificationType.success, false);
						}
						else {
							getServices().getAppController().serverErrorMessage(reason_code, "cant_save_page");
						}
					}
				}

				@Override
				public void onFinished(String responseText) {
					finishedCount++;
					updateLogic();
				}

				@Override
				public void onError(int reason_code) {
					this.reason_code = reason_code;
					errorCount++;
					updateLogic();
				}
			};

			appController.switchToPage(page, new ILoadListener() {
				@Override
				public void onFinishedLoading(Object obj) {
					page.getModules().clear();
					page.setHeight(EMPTY_PAGE_HEIGHT);

					IAppController appController = getServices().getAppController();
					appController.savePage(ireq);

					IUndoManager undoManager = appController.getUndoManager();
					undoManager.clear();
					undoManager.add("init", page.toXML());

					AppFrame appFrame = getServices().getAppController().getAppFrame();
					appFrame.getPresentation().setPage(page);
					appFrame.getProperties().setPage(page);
					appFrame.getModules().setPage(page);
					appFrame.getStyles().setPage(page);
				}

				@Override
				public void onError(String error) {
				    ireq.onError(IRequestListener.UKNOWN_CONNECTION_ERROR);
				}
			}, false);

			appController.saveContent(ireq);
		}
	}


	private Page addPageToList(String pageUrl, PageList pageList) {

		IAppController appController = getServices().getAppController();
		Page currentPage = appController.getCurrentPage();
		int currentIndex = pageList.indexOf(currentPage)+1;
		String foundName = pageList.generateUniquePageName();
		Page page = new Page(foundName, pageUrl);
		ActionUtils.ensureUniquePageId(page, getServices().getModel());
		pageList.insertBefore(currentIndex, page);
		return page;
	}

}
