package com.lorepo.iceditor.client.actions.utils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;
import org.mockito.Mockito;

import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class ActionUtilsTest {

	@Test
	public void TestGivenDuplicatePageIdWhenEnsuringUniquePageIdThenChangePageId(){
		Page page = new Page("Page 1", "");
		final String originalId = page.getId();
		
		Page duplicatePage = Mockito.mock(Page.class);
		when(duplicatePage.getId()).thenReturn(originalId);
		Page page2 = new Page("Page 2", "");
		Page page3 = new Page("Page 3", "");
		List<Page> pages = new ArrayList<Page>();
		pages.add(duplicatePage);
		pages.add(page2);
		pages.add(page3);
		
		Content lesson = Mockito.mock(Content.class);
		when(lesson.getAllPages()).thenReturn(pages);
		
		ActionUtils.ensureUniquePageId(page, lesson);

		assertFalse(page.equals(originalId));
		assertNotNull(page.getId());
		assertEquals(16, page.getId().length());
	}
}
