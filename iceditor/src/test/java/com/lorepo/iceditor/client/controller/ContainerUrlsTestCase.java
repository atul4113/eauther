package com.lorepo.iceditor.client.controller;
import java.util.ArrayList;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class ContainerUrlsTestCase {
	
	ContainerUrl urls; 
	ArrayList<String> testCases = new ArrayList<String>(); 
	String contentUrl = "contentURL/6166370446213120"; 
	String nextUrl = "nextURL/6166370446213120"; 
	String previewURLInNewTab = "previewURLInNewTab/6166370446213120"; 
	String abandonUrl = "abandonUrl/6166370446213120"; 
	String previewUrl = "previewUrl/6166370446213120"; 
	String favouriteModulesURL = "favouriteModulesURL/6166370446213120"; 
	AppController app; 
	
	@Before
	public void setup() {
		app = new AppController(); 
		ContainerUrl mockUrls = new ContainerUrl(); 
		app.setContainerUrl(mockUrls);
		
		urls = new ContainerUrl(); 
		testCases.add("mycontent/6166370446213120"); 
		testCases.add(""); 
	}
	
	
	@Test 
	public void settingAndGetingContentURL() {
		for (String testCase : testCases) {
			urls.setContentURL(testCase); 
			String t = urls.getContentURL(); 
			assertTrue(t.equals(testCase)); 
		} 
	} 
	
	
	@Test 
	public void settingAndGetingNextURL() {
		for (String testCase : testCases) {
			urls.setNextURL(testCase); 
			String t = urls.getNextURL(); 
			assertTrue(t.equals(testCase)); 
		} 
	} 
	
	
	@Test 
	public void settingAndGetingPreviewURLInNewTab() {
		for (String testCase : testCases) {
			urls.setPreviewURLInNewTab(testCase); 
			String t = urls.getPreviewURLInNewTab(); 
			assertTrue(t.equals(testCase)); 
		} 
	} 
	
	@Test 
	public void settingAndGetingAbandonUrl() {
		for (String testCase : testCases) {
			urls.setAbandonUrl(testCase); 
			String t = urls.getAbandonUrl(); 
			assertTrue(t.equals(testCase)); 
		} 
	} 
	
	@Test 
	public void settingAndGetingPreviewUrl() {
		for (String testCase : testCases) {
			urls.setPreviewUrl(testCase); 
			String t = urls.getPreviewUrl(); 
			assertTrue(t.equals(testCase)); 
		} 
	} 
	
	@Test 
	public void settingAndGetingFavouriteModulesURL() {
		for (String testCase : testCases) {
			urls.setFavouriteModulesURL(testCase); 
			String t = urls.getFavouriteModulesURL(); 
			assertTrue(t.equals(testCase)); 
		} 
	}
	
	

	@Test 
	public void settingAndGetingNullContentURL() {
		 urls.setContentURL(null); 
		 assertNull(urls.getContentURL()); 
	} 
	
	
	@Test 
	public void settingAndGetingNullNextURL() {
		 urls.setNextURL(null); 
		 assertNull(urls.getNextURL()); 
	} 
	
	@Test 
	public void settingAndGetingNullPreviewURLInNewTab() {
		 urls.setPreviewURLInNewTab(null); 
		 assertNull(urls.getPreviewURLInNewTab()); 
	} 
	
	@Test 
	public void settingAndGetingNullAbandonUrl() {
		 urls.setAbandonUrl(null); 
		 assertNull(urls.getAbandonUrl()); 
	} 
	
	
	@Test 
	public void settingAndGetingNullPreviewUrl() {
		 urls.setPreviewUrl(null); 
		 assertNull(urls.getPreviewUrl()); 
	} 
	
	@Test 
	public void settingAndGetingNullFavouriteModulesURL() {
		 urls.setFavouriteModulesURL(null); 
		 assertNull(urls.getFavouriteModulesURL()); 
	} 
	
	@Test
	public void settingAndGetingAppControllerContentURL() {
		app.setContent(contentUrl);
		assertTrue(contentUrl.equals(app.getContentUrl())); 
	}
	
	@Test
	public void settingAndGetingAppControllerPreviewURLInNewTab() {
		app.setPreviewUrlInNewTab(previewURLInNewTab);
		assertTrue(previewURLInNewTab.equals(app.getPreviewUrlInNewTab())); 
	}
	
	@Test
	public void settingAndGetingAppControllerAbandonUrl() {
		app.setAbandonUrl(abandonUrl);
		assertTrue(abandonUrl.equals(app.getAbandonUrl())); 
	}
	
	@Test
	public void settingAndGetingAppControllerPreviewUrl() {
		app.setPreviewUrl(abandonUrl);
		assertTrue(abandonUrl.equals(app.getPreviewUrl())); 
	}
	
	@Test
	public void settingAndGetingAppControllerFavouriteModulesURL() {
		app.saveFavouriteModulesURL(abandonUrl);
		assertTrue(abandonUrl.equals(app.getFavouriteModulesURL())); 
	}
	
	@Test
	public void settingAndGetingAppControllerNextURL() {
		app.setNextURL(abandonUrl);
		assertTrue(abandonUrl.equals(app.getNextURL())); 
	}
}
