package com.lorepo.iceditor.client.actions.utils;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.icf.utils.UUID;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class ActionUtils {
	
	public static void ensureUniquePageId(Page page, Content content) {
		List<String> ids = new ArrayList<String>();
		for (Page contentPage: content.getAllPages()) {
			ids.add(contentPage.getId());
		}
		while(ids.contains(page.getId())) {
			page.setId(UUID.uuid(16));
		}
	}
}
