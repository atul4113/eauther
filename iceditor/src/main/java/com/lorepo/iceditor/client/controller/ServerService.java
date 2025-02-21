package com.lorepo.iceditor.client.controller;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.IServerService;

public class ServerService implements IServerService {

	private static final String CREATE_URL_PATH = "/editor/api/addNewPage";
	
	private IAppController appController = null;

	
	@Override
	public void addPage(String templateUrl, final IRequestListener listener) throws RequestException {

		String url = createURL(templateUrl);
		
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, URL.encode(url));
		builder.setHeader("Content-Type", "text/xml");

		builder.sendRequest("", new RequestCallback() {
			
			@Override
			public void onResponseReceived(Request request, Response response) {
				if(response.getStatusCode() == 200){
					listener.onFinished(response.getText());
				}
				else{
					listener.onError(response.getStatusCode());
				}
			}
			
			@Override
			public void onError(Request request, Throwable exception) {
				listener.onError(IRequestListener.UKNOWN_CONNECTION_ERROR);
			}
		});
		
	}


	public String createURL(String templateUrl) {
		

		String url = CREATE_URL_PATH;
		String connector;
		
		if (appController != null) {
			url += "?content_file=" + appController.getContentUrl();
			connector = "&";
		}
		else {
			connector = "?";
		}
		
		
		if(!templateUrl.isEmpty()){
			url = url + connector + "page=" + templateUrl;
		}
		
		return url;
	}


	@Override
	public void saveFile(String url, String content, final IRequestListener listener) {
			
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, URL.encode(url));
		builder.setHeader("Content-Type", "text/xml");
	
		try {
			builder.sendRequest(content, new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() >= 400){
						listener.onError(response.getStatusCode());
					}
					else{
						listener.onFinished(response.getText());
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					listener.onError(999);
				}
			});
		} catch (RequestException e) {
			listener.onError(999);
		}		
			
	}


	@Override
	public void saveFileInBackground(String url, String content, final IRequestListener listener) {
			
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, URL.encode(url));
		builder.setHeader("Content-Type", "text/xml");
	
		try {
			builder.sendRequest(content, new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() >= 400){
						listener.onError(response.getStatusCode());
					}
					else{
						listener.onFinished(response.getText());
					}					
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					listener.onError(999);
				}
			});
		} catch (RequestException e) {
		}		
			
	}


	@Override
	public void load(String url, IRequestListener listener) {
	}


	public void setAppController(IAppController appController) {
		this.appController = appController;
	}

}
