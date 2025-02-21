package com.lorepo.iceditor.client.actions.mockup;

import java.util.HashMap;

import com.google.gwt.http.client.RequestException;
import com.lorepo.iceditor.client.actions.api.IServerService;

public class ServerServiceMockup implements IServerService {

	private static String NEW_FILE_URL = "/file/1";
	private HashMap<String, String> files = new HashMap<String, String>();
	
	
	@Override
	public void addPage(String templateUrl, IRequestListener listener) throws RequestException {

		files.put(NEW_FILE_URL, "");
		listener.onFinished(NEW_FILE_URL);
	}

	
	@Override
	public void saveFile(String url, String content, IRequestListener listener) {

		files.put(url, content);
		listener.onFinished("");
	}

	
	@Override
	public void load(String url, IRequestListener listener) {

		String xml = files.get(url);
		listener.onFinished(xml);
	}


	@Override
	public void saveFileInBackground(String url, String content, IRequestListener listener) {
		// TODO Auto-generated method stub
		
	}
}
