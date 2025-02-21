package com.lorepo.iceditor.client.ui.widgets.docs;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.Callback;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;

public class DocumentationService {
	private final static String mAuthorURL = "https://lorepocorporate.appspot.com";
	private static String lang = "en";
	
	private static Map<String, String> URLS = new HashMap<String, String>(); /* <key: name, value: URL> */
	private static Map<String, DocumentationPage> PAGES = new HashMap<String, DocumentationPage>();
	private static Map<String, DocumentationSection> SECTIONS = new HashMap<String, DocumentationSection>();

	static {
		URLS.put("Check Button", "Check-and-Reset-buttons");
		URLS.put("Check Counter", "Check-counter");
		URLS.put("ErrorCounter", "Check-counter");
		URLS.put("Page Progress", "Page-progress");
		URLS.put("Report", "Lesson-report");
		URLS.put("nextPageButton", "Next-Page-Button");
		URLS.put("prevPageButton", "Previous-Page-Button");
		URLS.put("resetButton", "Check-and-Reset-buttons");
		URLS.put("cancelButton", "Close-Popup-button");
		URLS.put("popupButton", "Open-Popup-Button");
		URLS.put("gotoPageButton", "Go-To-Page-Button");
		URLS.put("Viewer_3D", "3D-Viewer");
		URLS.put("eKeyboard", "eKeyboard");
		URLS.put("Image_Viewer_Public", "Image-Viewer");
		URLS.put("Image_Viewer_Button_Controlled_Public", "Image-Viewer-Button-Controlled");
		URLS.put("LearnPen", "LearnPen-Drawing");
		URLS.put("LearnPen_Data", "LearnPen-Data");
		URLS.put("LearnPen_Report", "LearnPen-Report");
		URLS.put("gamememo", "Memo-Game");
		URLS.put("MultiAudio", "MultiAudio");
		URLS.put("multiplegap", "Multiple-Gap");
		URLS.put("Navigation_Bar", "Navigation-bar");
		URLS.put("Paragraph_Keyboard", "Paragraph-eKeyboard");
		URLS.put("PointsLines", "Points-and-Lines");
		URLS.put("SVG2", "SVG");
		URLS.put("Table_Of_Contents", "Table-of-Contents");
		URLS.put("text_identification", "Text-Identification");
		URLS.put("TextAudio", "TextAudio");
		URLS.put("TrueFalse", "TrueFalse");
		URLS.put("YouTube_Addon", "YouTube");
		URLS.put("Page", "Page-management");
	}
	
	public static void setLang (String language) {
		if (language.equalsIgnoreCase("mx")) {
			lang = "es";
		} else {
			lang = language;
		}
		PAGES.clear();
		SECTIONS.clear();
	}
	
	public static void getPage (String name, Callback<DocumentationPage, String> callback, boolean isPrivate) {
		if (!isPrivate) {
			String url = nameToUrl(name);
			if (PAGES.containsKey(url)){
				callback.onSuccess(PAGES.get(url));
			} else {
				getPageFromMAuthor(name, url, callback);
			}
		} else {
			getPageFromMAuthor(name, name, callback);
		}
	}
	
	public static void getSection (String name, Callback<DocumentationSection, String> callback) {
		String url = nameToUrl(name);
		if (SECTIONS.containsKey(url)){
			callback.onSuccess(SECTIONS.get(url));
		} else {
			getSectionFromMAuthor(name, url, callback);
		}
	}
	
	private static native String clearAndSplitCamelCase (String s) /*-{
		var sepReg = new RegExp("_", "g"),
			reg1 = new RegExp("([A-Z])([A-Z][a-z])", "g"),
			reg2 = new RegExp("([^A-Z])([A-Z])", "g"),
			reg3 = new RegExp("([A-z])([^A-z])", "g"),
			wsReg = new RegExp("\\s+", "g");
				
		return s.replace(sepReg, " ").
				 replace(reg1, "$1 $2").
				 replace(reg2, "$1 $2").
				 replace(reg3, "$1 $2").
				 replace(wsReg, " ");
	}-*/;
	
	private static String nameToUrl (String name) {
		if (URLS.containsKey(name)) {
			return URLS.get(name);
		} else {
			String url = clearAndSplitCamelCase(name);
			url = url.replace(" ", "-");
			url = Character.toUpperCase(url.charAt(0)) + url.substring(1);
			return url;
		}
	}
	
	private static void getPageFromMAuthor (final String name, final String url, final Callback<DocumentationPage, String> callback) {
		final String docsURL = mAuthorURL + "/doc/api/" + lang + "/page/" + url;
		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, docsURL);
		
		try {
			builder.sendRequest(null, new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if (response.getStatusCode() == 200) {
						String result = response.getText();
						DocumentationPage page = new DocumentationPage(name, result);
						PAGES.put(url, page);
						callback.onSuccess(page);
					} else {
						callback.onFailure(response.getStatusText());
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					callback.onFailure(exception.getMessage());
					
				}
			});
		} catch (RequestException e) {
			callback.onFailure(e.getMessage());
		}
	}
	
	private static void getSectionFromMAuthor (final String name, final String url, final Callback<DocumentationSection, String> callback) {
		final String docsSectionURL = mAuthorURL + "/doc/api/" + lang + "/section/" + url;
		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET, docsSectionURL);
		
		try {
			builder.sendRequest(null, new RequestCallback() {
				
				@Override
				public void onResponseReceived(Request request, Response response) {
					if (response.getStatusCode() == 200) {
						String result = response.getText();
						DocumentationSection section = new DocumentationSection(name, result);
						SECTIONS.put(url, section);
						callback.onSuccess(section);
					} else {
						callback.onFailure(response.getStatusText());
					}
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					callback.onFailure(exception.getMessage());
					
				}
			});
		} catch (RequestException e) {
			callback.onFailure(e.getMessage());
		}
	}
}
