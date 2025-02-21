package com.lorepo.iceditor.client.actions.api;

import com.google.gwt.http.client.RequestException;


public interface IServerService {

	public interface IRequestListener{
		public static final int UKNOWN_CONNECTION_ERROR = -999;
		public void onFinished(String responseText);
		public void onError(int reason_code);
	}
	
	public void addPage(String templateUrl, IRequestListener listener) throws RequestException;
	public void saveFile(String url, String content, IRequestListener listener);
	public void load(String url, IRequestListener listener);
	public void saveFileInBackground(String url, String content, IRequestListener listener);

}
