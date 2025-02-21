package com.lorepo.iceditor.client.actions;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.content.FavouriteModulesListWidget;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class EditFavouriteModules extends AbstractAction {

	private FavouriteModulesListWidget widget = getServices().getAppController().getAppFrame().getFavouriteModules();
	private AppController appController;
	
	public EditFavouriteModules(AppController controller) {
		super(controller);
		this.appController = controller;
	}

	public static native void addDraggableToFavouriteModule() /*-{
	  $wnd.addDraggableToFavouriteModule();
	}-*/;
	
	public void execute() {
		if (WidgetLockerController.isVisible()) {
			return;
		}
				
		widget.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				appController.setFavouriteModules(widget.getFavouriteModules());
				appController.updateFavouriteModules();
				saveFavouriteModules();
				
				widget.hide();
				addDraggableToFavouriteModule();
			}
			
			@Override
			public void onApply() {
				getServices().getAppController().setFavouriteModules(widget.getFavouriteModules());
				getServices().getAppController().updateFavouriteModules();
				saveFavouriteModules();
			}
		});
		
		widget.show();
		WidgetLockerController.show();
	}
	
	private void saveFavouriteModules() {
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, URL.encode(appController.getFavouriteModulesURL()));
		JSONArray jsonRPC = new JSONArray();
		JSONObject jsonObject = new JSONObject();
		int i = 0;

		for (ModuleInfo key : appController.getFavouriteModules().values()) {
			jsonRPC.set(i, new JSONString(key.originalName));
			i++;
		}
		
		jsonObject.put("fav_modules", jsonRPC);
		
		String postData = jsonObject.toString(); 
		builder.setHeader("Content-type", "application/json");
		
		try {
			builder.sendRequest(postData, new RequestCallback() {
				@Override
				public void onResponseReceived(Request request, Response response) {
					if (response.getStatusCode() == 401) {
						appController.getAppFrame().getNotifications().addMessage(DictionaryWrapper.get("can_not_save_fav_modules"), NotificationType.error, false);
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {

				}
			});
		} catch(RequestException e) {}
	}
}
