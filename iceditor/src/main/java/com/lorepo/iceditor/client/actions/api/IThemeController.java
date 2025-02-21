package com.lorepo.iceditor.client.actions.api;

import com.lorepo.icplayer.client.model.Content;

public interface IThemeController {

	public String getPageUrlByNameOrFirst(String pageName);
	public Content getTheme();
}
