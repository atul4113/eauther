package com.lorepo.iceditor.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONParser;
import com.lorepo.icf.utils.JavaScriptUtils;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class EditorEntryPoint implements EntryPoint{

	/** JavaScript object representing this java object */
	private static JavaScriptObject	jsObject;

	private static EditorApp	theApplication;
	
	/**
	 * This is the entry point method.
	 */
	public void onModuleLoad() {

		jsObject = JavaScriptObject.createFunction();
		initJavaScriptAPI(this);
	}
	
	
	/**
	 * Init Javascript API
	 */
	private static native void initJavaScriptAPI(EditorEntryPoint x) /*-{
		
		// CreateEditor
		$wnd.icCreateEditor = function(config) {
			var editor = @com.lorepo.iceditor.client.EditorEntryPoint::createAppEditor(Lcom/google/gwt/core/client/JavaScriptObject;)(config);
		  	editor.load = function(url){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::load(Ljava/lang/String;)(url);
			};
		  	editor.setNextUrl = function(url){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::setNextUrl(Ljava/lang/String;)(url);
			};
			editor.setPreviewUrlInNewTab = function(url){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::setPreviewUrlInNewTab(Ljava/lang/String;)(url);
			}
			editor.setPreviewUrl = function(url){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::setPreviewUrl(Ljava/lang/String;)(url);
			}
		  	editor.setAbandonUrl = function(url){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::setAbandonUrl(Ljava/lang/String;)(url);
			};
		  	editor.setTitle = function(title, subTitle){
		    	x.@com.lorepo.iceditor.client.EditorEntryPoint::setEditorTitle(Ljava/lang/String;Ljava/lang/String;)(title, subTitle);
			};
			editor.setLogoUrl = function(url) {
				x.@com.lorepo.iceditor.client.EditorEntryPoint::setLogoUrl(Ljava/lang/String;)(url);
			};

			editor.setRenderedView = function(shouldRenderView) {
				x.@com.lorepo.iceditor.client.EditorEntryPoint::setRenderedView(Ljava/lang/String;)(shouldRenderView);
			}
			editor.saveShouldRender = function(url) {
				x.@com.lorepo.iceditor.client.EditorEntryPoint::saveShouldRender(Ljava/lang/String;)(url);
			}

			editor.setFavouriteModules = function(favouriteModules) {
				x.@com.lorepo.iceditor.client.EditorEntryPoint::setFavouriteModules(Ljava/lang/String;)(favouriteModules);
			};
			editor.saveFavouriteModulesURL = function(saveFavouriteModulesURL) {
				x.@com.lorepo.iceditor.client.EditorEntryPoint::saveFavouriteModulesURL(Ljava/lang/String;)(saveFavouriteModulesURL);
			};

			return editor;
		}

		// Call App loaded function
		if(typeof $wnd.iceOnAppLoaded == 'function') {
		  $wnd.iceOnAppLoaded();	
		}
	}-*/;

	
	/**
	 * createPlayer js interface
	 */
	public static JavaScriptObject createAppEditor(JavaScriptObject jsConfig) {
		EditorConfig config = new EditorConfig();
		if(jsConfig != null){
			config.apiURL = JavaScriptUtils.getArrayItemByKey(jsConfig, "apiURL");
			config.analyticsId = JavaScriptUtils.getArrayItemByKey(jsConfig, "analytics");

			String showTemplates = JavaScriptUtils.getArrayItemByKey(jsConfig, "showTemplates");
			if (showTemplates.equals("false")) {
				config.showTemplates = false;
			}
			
			config.logoUrl = JavaScriptUtils.getArrayItemByKey(jsConfig, "logoURL");
			config.parseExcludeAddons(JavaScriptUtils.getArrayItemByKey(jsConfig, "excludeAddons"));
			
			config.lang = JavaScriptUtils.getArrayItemByKey(jsConfig, "lang");
		}
		theApplication = new EditorApp(config);
		return jsObject;
	}
	
	
	/**
	 * Load assessment from this url
	 * 
	 * @param url
	 */
	@SuppressWarnings("static-method")
	private void load(String id) {
		theApplication.load(id);
	}
	
	@SuppressWarnings("static-method")
	private void setNextUrl(String url) {
		theApplication.setNextUrl(url);
	}
	
	@SuppressWarnings("static-method")
	private void setPreviewUrlInNewTab(String url) {
		theApplication.setPreviewUrlInNewTab(url);
	}
	
	@SuppressWarnings("static-method")
	private void setPreviewUrl(String url) {
		theApplication.setPreviewUrl(url);
	}
	
	@SuppressWarnings("static-method")
	private void setAbandonUrl(String url) {
		theApplication.setAbandonUrl(url);
	}
	
	@SuppressWarnings("static-method")
	private void setEditorTitle(String title, String subTitle){
        theApplication.setEditorTitle(title, subTitle);
    }
	
	@SuppressWarnings("static-method")
	private void setLogoUrl(String url){
        theApplication.setLogoUrl(url);
    }
	
	@SuppressWarnings("static-method")
	private void setRenderedView(String shouldRender) {
        theApplication.setRenderedView(Boolean.parseBoolean(shouldRender));
	}
	
	@SuppressWarnings("static-method")
	private void saveShouldRender(String url) {
        theApplication.saveShouldRenderURL(url);
	}
	
	@SuppressWarnings("static-method")
	private void saveFavouriteModulesURL(String url){
        theApplication.saveFavouriteModulesURL(url);
    }

	@SuppressWarnings("static-method")
	private void setFavouriteModules(String modules) {
		List<String> favouriteModules = new ArrayList<String>();

		if (modules.equals("")) {
			// Names of modules occur in ModulesInfoUtils, names of addons in AddonDescriptor (with suffix _name)
			List<String> defaultModules = 
					Arrays.asList(
						"text_menu", 
						"choice_menu",
						"image_menu",
						"ordering_menu",
						"source_list_menu",
						"Connection_name", 
						"YouTube_Addon_name", 
						"gamememo_name", 
						"text_identification_name"
					);
			
			favouriteModules.addAll(defaultModules);
		} else {
			JSONArray modulesArray = JSONParser.parseStrict(modules).isArray();
			
			for(int i = 0; i < modulesArray.size(); i++) {
				favouriteModules.add(modulesArray.get(i).isString().stringValue());
			}
		}

		Collections.sort(favouriteModules);
		
		theApplication.setFavouriteModules(favouriteModules);
    }
}