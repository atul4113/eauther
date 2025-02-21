package com.lorepo.iceditor.client;

import java.util.Arrays;
import java.util.List;

import com.lorepo.iceditor.client.module.properties.ModuleDefaultPropertiesService;
import com.lorepo.iceditor.client.ui.widgets.docs.DocumentationService;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class EditorLanguage {
	private static String langauge = "en";
	private static List<String> languages = Arrays.asList(new String[] {"en", "fr", "mx", "pl", "es", "bl"});
	
	public static void setLanguage (String lang){
		if (languages.contains(lang)) {
			langauge = lang;
			DictionaryWrapper.setLang(langauge);
			DocumentationService.setLang(langauge);
			ModuleDefaultPropertiesService.init(langauge);
		}
	};
	
	public static String getLanguage () {
		return langauge;
	}
}
