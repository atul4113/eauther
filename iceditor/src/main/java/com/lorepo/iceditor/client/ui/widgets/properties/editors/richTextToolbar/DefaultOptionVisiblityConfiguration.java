package com.lorepo.iceditor.client.ui.widgets.properties.editors.richTextToolbar;

import java.util.HashMap;
import java.util.Map;

public class DefaultOptionVisiblityConfiguration implements VisibilityConfiguration {
	public final static String insertAudioKey = "insertAudio"; 
	
	private Map<String, Boolean> configuration;
	
	public DefaultOptionVisiblityConfiguration() {
		configuration = new HashMap<String, Boolean>();
		
		configuration.put(insertAudioKey, getInsertAudioVisibility());
	}
	
	public Map<String, Boolean> getConfiguration() {
		return configuration;
	}
	
	protected Boolean getInsertAudioVisibility() {
		return false;
	}
}
