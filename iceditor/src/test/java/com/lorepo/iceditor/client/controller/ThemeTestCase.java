package com.lorepo.iceditor.client.controller;

import static org.junit.Assert.assertEquals;

import java.io.IOException;

import org.junit.Test;

import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;

public class ThemeTestCase {

	@Test
	public void createURLNoTheme() throws IOException {
		
		ThemeController theme = new ThemeController(null);
		String url = theme.getPageUrlByNameOrFirst("");

		assertEquals("", url);
	}
	
	@Test
	public void createURLWithThemeDefaultPage() throws IOException {
		
		ThemeController theme = new ThemeController(null);
		Content content = createTheme();
		theme.setTheme(content);
		String url = theme.getPageUrlByNameOrFirst("");

		assertEquals("page1", url);
	}

	
	@Test
	public void createURLWithThemePage2() throws IOException {
		
		ThemeController theme = new ThemeController(null);
		Content content = createTheme();
		theme.setTheme(content);
		String url = theme.getPageUrlByNameOrFirst("Page 2");

		assertEquals("page2", url);
	}

	
	@Test
	public void createURLWithThemeDefaultPage3() throws IOException {
		
		ThemeController theme = new ThemeController(null);
		Content content = createTheme();
		theme.setTheme(content);
		String url = theme.getPageUrlByNameOrFirst(null);

		assertEquals("page1", url);
	}

	
	private static Content createTheme() {
		
		Content theme = new Content();
		
		theme.getPages().add(new Page("Page 1", "page1"));
		theme.getPages().add(new Page("Page 2", "page2"));
		theme.getPages().add(new Page("Page 3", "page3"));
		
		return theme;
	}
	
}
