package com.lorepo.iceditor.client;

import java.util.HashSet;
import java.util.Set;

public class EditorConfig {

	public String apiURL;
	public String analyticsId;
	public boolean showTemplates = true;
	public String logoUrl;
	public Set<String> excludeAddons = new HashSet<String>();
	public String lang;
	
	public void parseExcludeAddons(String value) {
		String[] tokens = value.split(",");
		for(int i = 0; i < tokens.length; i++){
			String moduleId = tokens[i].trim();
			if(moduleId.length() > 0){
				excludeAddons.add(moduleId);
			}
		}
	}
}
