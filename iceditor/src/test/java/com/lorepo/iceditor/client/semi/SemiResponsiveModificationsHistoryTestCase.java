package com.lorepo.iceditor.client.semi;

import static org.junit.Assert.*;

import java.util.ArrayList;

import org.junit.Before;
import org.junit.Test;

import com.lorepo.iceditor.client.semi.responsive.SemiResponsiveModificationsHistory;

public class SemiResponsiveModificationsHistoryTestCase {
	private ArrayList<String> pages;
	private ArrayList<String> layouts;
	
	@Before
	public void setUp() {
		 pages = new ArrayList<String>();
		 pages.add("ID1");
		 pages.add("ID2");
		 pages.add("ID3");
		 
		 layouts = new ArrayList<String>();
		 layouts.add("LAYOUT1");
		 layouts.add("LAYOUT2");
	}
	
	@Test
	public void AddingPagesTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(0)));
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(1)));
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(2)));
	}
	
	@Test
	public void WasPageAddedTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		String pageNotInHistory = "NOT_IN_HISTORY";
		
		assertTrue(SemiResponsiveModificationsHistory.wasPageAdded(pages.get(0)));
		assertTrue(SemiResponsiveModificationsHistory.wasPageAdded(pages.get(1)));
		assertTrue(SemiResponsiveModificationsHistory.wasPageAdded(pages.get(2)));
		assertFalse(SemiResponsiveModificationsHistory.wasPageAdded(pageNotInHistory));
	}
	
	@Test
	public void RemovingPagesTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		
		SemiResponsiveModificationsHistory.removePage(pages.get(0));
		
		assertFalse(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(0)));
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(1)));
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(pages.get(2)));
	}
	
	@Test
	public void addLayoutTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		SemiResponsiveModificationsHistory.addNewSemiResponsiveLayout(pages.get(0), layouts.get(0));
		
		assertTrue(SemiResponsiveModificationsHistory.layoutAdded.contains(layouts.get(0)));
	}
	
	@Test
	public void checkIfLayoutWasVisitedTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		SemiResponsiveModificationsHistory.markAsVisited(pages.get(0), layouts.get(0));
		
		assertTrue(SemiResponsiveModificationsHistory.layoutWasVisited(pages.get(0), layouts.get(0)));
	}
	
	@Test
	public void settingLastSeenTemplateTest(){
		for (String id : pages){
			SemiResponsiveModificationsHistory.addNewPage(id);
		}
		
		SemiResponsiveModificationsHistory.addNewSemiResponsiveLayout(pages.get(0), layouts.get(0));		
		SemiResponsiveModificationsHistory.setLastSeen(pages.get(0), layouts.get(0));
		SemiResponsiveModificationsHistory.addNewSemiResponsiveLayout(pages.get(0), layouts.get(1));
		
		assertEquals(SemiResponsiveModificationsHistory.getLastSeen(pages.get(0)), layouts.get(0));
	}
	
	@Test
	public void duplicatingPageTest() {
		String oldPage = pages.get(0);
		String duplicatedPage = pages.get(1);
		String visitedLayout = layouts.get(0);
		
		SemiResponsiveModificationsHistory.addNewPage(oldPage);
		SemiResponsiveModificationsHistory.addNewSemiResponsiveLayout(oldPage, visitedLayout);		
		
		SemiResponsiveModificationsHistory.setLastSeen(oldPage, visitedLayout);
		SemiResponsiveModificationsHistory.markAsVisited(oldPage, visitedLayout);
		
		SemiResponsiveModificationsHistory.duplicatePage(oldPage, duplicatedPage);
		
		assertTrue(SemiResponsiveModificationsHistory.pageAdded.contains(duplicatedPage));
		assertEquals(visitedLayout, SemiResponsiveModificationsHistory.getLastSeen(duplicatedPage));
		assertTrue(SemiResponsiveModificationsHistory.layoutWasVisited(duplicatedPage, visitedLayout));		
	}
}
