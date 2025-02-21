package com.lorepo.iceditor.client.ui.widgets.properties.editors.richTextToolbar;

public class ConfigurationManager {
	public static VisibilityConfiguration getConfiguration(String moduleType) {
		if (moduleType.equals("Text")) {
			return new TextVisibilityConfiguration();
		}
		
		return new DefaultOptionVisiblityConfiguration();
	}
}
