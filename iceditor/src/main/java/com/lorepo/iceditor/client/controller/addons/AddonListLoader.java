package com.lorepo.iceditor.client.controller.addons;

import java.util.List;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icplayer.client.model.addon.AddonEntry;

public class AddonListLoader {

	private String addonsListUrl = "/editor/api/addons";
	private List<AddonEntry> entries;
	
	
	public AddonListLoader(String apiURL) {
		if(apiURL != null && !apiURL.isEmpty()){
			addonsListUrl = apiURL + "/addons";
		}
	}


	public void load(final ILoadListener listener) {

		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, addonsListUrl);

		try {
			builder.sendRequest("", new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if(response.getStatusCode() == 200){
						parseJsonData(response.getText());
						listener.onFinishedLoading(this);
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
				}
			});
		} catch (RequestException e) {
		}		
		
	}
	
	
	protected void parseJsonData(String text) {
		
		AddonsJsonParser addonsParser = AddonsJsonParser.parse(text);
		entries = addonsParser.toArray();
	}
	
	
	public List<AddonEntry>	getEntries(){
		return entries;
	}

}
