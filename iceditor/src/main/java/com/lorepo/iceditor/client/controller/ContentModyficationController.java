package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.HashMap;

import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.ClosingEvent;
import com.google.gwt.user.client.Window.ClosingHandler;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.page.Page;

public class ContentModyficationController {
	private IAppController appController;
	private IActionService actionService;

	private HashMap<String, Boolean> pagesModifiedFlag = new HashMap<String, Boolean>();
	private ArrayList<Page> unsavedPages = new ArrayList<Page>();
	private boolean isModified = false;
	private boolean isContentModified = false;
	private int errorsCount = 0;
	private int finishedCount = 0;
	private HandlerRegistration closingHandler;

	public ContentModyficationController(IAppController appController) {
		this.appController = appController;
		
		connectHandlers();
	}
	
	private void connectHandlers() {
	    closingHandler = Window.addWindowClosingHandler(new ClosingHandler() {
			public void onWindowClosing(ClosingEvent event) {
				if (isModified()) {
					Page currentPage = appController.getCurrentPage();
					
					if (currentPage == null) {
						return;
					}
					
					final NotificationsWidget notifications = appController.getAppFrame().getNotifications();
					notifications.addMessage(DictionaryWrapper.get("please_wait"), NotificationType.notice, false);

					IRequestListener ireql = new IRequestListener() {
						@Override
						public void onFinished(String responseText) {
							notifications.addMessage(DictionaryWrapper.get("page_saved"), NotificationType.success, false);
						}
						
						@Override
						public void onError(int server_error) {
							actionService.getAppController().serverErrorMessage(server_error, "cant_save_page");
						}
					};
					
					appController.savePage(ireql);
				
				}
			}
		});

	    Timer timer = new Timer() {
	    	public void run() {
	    		savePageIfModified(null);
	        }
	    };

	    // Schedule the timer to run every 60 seconds
	    timer.scheduleRepeating(60*1000);
	}
	
	public boolean isModified() {
		return isModified;
	}
	
	public void setModified(boolean isModified) {
		setModified(isModified, appController.getCurrentPage().getId());
	}
	
	public boolean isContentModified() {
		return isContentModified;
	}
	
	public void setContentAsModified(boolean isModified) {
		this.isContentModified = isModified;
	}
	
	public void setModified(boolean isModified, String pageID) {
		pagesModifiedFlag.put(pageID, Boolean.valueOf(isModified));
		boolean isAnyModified = isModified;

		if (!isAnyModified) {
			for (Boolean curently_modified : pagesModifiedFlag.values()) {
				if (curently_modified == Boolean.TRUE) {
					isAnyModified = true;
					break;
				}
			}
		}

		this.isModified = isAnyModified;	
	}
	
	public void setActionService(IActionService actionService) {
		this.actionService = actionService;

		actionService.registerHandler(Handlers.CloseEditorHandler, closingHandler);
	}
	
	public void savePageIfModified(final IRequestListener listener) {
		Page page = appController.getCurrentPage();
		
		if (page == null) {
			return;
		}
		
		if (!isModified()) {
			if (listener != null) {
				listener.onFinished(null);
			}
			
			checkAllPagesSaved();
			return;
		}

		final Page pageBeingSaved = page;
		String xml = page.toXML();

		actionService.getServerService().saveFileInBackground(page.getURL(), xml, new IRequestListener() {
			public void onFinished(String responseText) {
				setModified(false, pageBeingSaved.getId());

				appController.getAppFrame().getNotifications().addMessage(DictionaryWrapper.get("page_saved"), NotificationType.success, false);
				
				if (listener != null) {
					listener.onFinished(null);
				}
				
				checkAllPagesSaved();
			}
			public void onError(int server_error) {
				actionService.getAppController().serverErrorMessage(server_error, "cant_save_page");
				
				if (listener != null) {
					listener.onError(0);
				}
				
				unsavedPages.add(pageBeingSaved);
			}
		});
	}
	
	public void checkAllPagesSaved() {
		final int unsavedPagesLength = unsavedPages.size();

		if (unsavedPagesLength > 0) {
			finishedCount = 0 ;
			errorsCount = 0;

			for (final Page unsavedPage : unsavedPages) {
				String xml = unsavedPage.toXML();

				actionService.getServerService().saveFileInBackground(unsavedPage.getURL(), xml, new IRequestListener() {
					private void onUpdate() {
						if (finishedCount + errorsCount == unsavedPagesLength) {
							if (errorsCount == 0) {
								setModified(false);
								appController.getAppFrame().getNotifications().addMessage(DictionaryWrapper.get("page_saved"), NotificationType.success, false);
							}
						}
					}

					public void onFinished(String responseText) {
						unsavedPages.remove(unsavedPage);
						setModified(false, unsavedPage.getId());
						finishedCount++;
						onUpdate();
					}

					public void onError(int server_error) {
						errorsCount++;
						onUpdate();
					}
				});
			}
		}
	}
	
	public boolean isPageModified(String pageID) {
		if (pagesModifiedFlag.containsKey(pageID)) {
			return pagesModifiedFlag.get(pageID);
		}

		return false;
	}
}
