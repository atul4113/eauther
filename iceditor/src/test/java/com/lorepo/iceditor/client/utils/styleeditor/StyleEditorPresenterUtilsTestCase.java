package com.lorepo.iceditor.client.utils.styleeditor;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenterUtils;

public class StyleEditorPresenterUtilsTestCase {
	@Test
	public void shouldAddPreviousButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_previous_page_blue", "previouspage"));
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_prev_page_blue", "previouspage"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("previouspage_blue", "previouspage"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_previous_pageblue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_prevpage_blue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_prevpageblue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("buttonprevpage_blue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("prevpage_blue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("previous_page_blue", "previouspage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("previouspageblue", "previouspage"));
	}
	
	@Test
	public void shouldAddNextButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_next_page_blue", "nextpage"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("nextpage_blue", "nextpage"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_next_pageblue", "nextpage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_nextpageblue", "nextpage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("buttonnextpage_blue", "nextpage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("next_page_blue", "nextpage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("nextpageblue", "nextpage"));
	}
	
	@Test
	public void shouldAddResetButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_reset_blue", "reset"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("reset_blue", "reset"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("buttonresetblue", "reset"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_resetblue", "reset"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("buttonreset_blue", "reset"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("resetblue", "reset"));
	}
	
	@Test
	public void shouldAddGoToPageButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_go_to_page_blue", "gotopage"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("gotopage_blue", "gotopage"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_gotopage_pageblue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_gotopagepageblue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("buttongotopagepage_blue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("go_to_page_blue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("go_topage_blue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("goto_page_blue", "gotopage"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("gotopageblue", "gotopage"));
	}
	
	@Test
	public void shouldAddOpenPopupButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_open_popup_blue", "openpopup"));
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_popup_blue", "openpopup"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("openpopup_blue", "openpopup"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_openpopup_blue", "openpopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("open_popup_blue", "openpopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("popup", "openpopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("popup_blue", "openpopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("popupblue", "openpopup"));
	}
	
	@Test
	public void shouldAddClosePopupButtonClassTest() {
		// Compatibility		
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_close_popup_blue", "closepopup"));
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("button_cancel_popup_blue", "closepopup"));
		
		// Current naming
		assertTrue(StyleEditorPresenterUtils.shouldAddButtonClass("closepopup_blue", "closepopup"));
		
		// Should not add below classes
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_close_popupblue", "closepopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("close_popup_blue", "closepopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("cancel", "closepopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("cancel_blue", "closepopup"));
		assertFalse(StyleEditorPresenterUtils.shouldAddButtonClass("button_cancelblue", "closepopup"));
	}
	
	@Test
	public void getOpenPopupClassNamePrefix() {
		StyledModuleMockup moduleMockup = new StyledModuleMockup();
		moduleMockup.setClassNamePrefix("popup");
		
		assertEquals("openpopup", StyleEditorPresenterUtils.getModuleClassNamePrefix(moduleMockup));
	}
	
	@Test
	public void getClosePopupClassNamePrefix() {
		StyledModuleMockup moduleMockup = new StyledModuleMockup();
		moduleMockup.setClassNamePrefix("cancel");
		
		assertEquals("closepopup", StyleEditorPresenterUtils.getModuleClassNamePrefix(moduleMockup));
	}
	
	@Test
	public void getPreviousPagePopupClassNamePrefix() {
		StyledModuleMockup moduleMockup = new StyledModuleMockup();
		moduleMockup.setClassNamePrefix("prevPage");
		
		StyleEditorPresenterUtils.getModuleClassNamePrefix(moduleMockup);
		
		assertEquals("previouspage", StyleEditorPresenterUtils.getModuleClassNamePrefix(moduleMockup));
	}
	
	@Test
	public void getClassNamePrefix() {
		StyledModuleMockup moduleMockup = new StyledModuleMockup();
		moduleMockup.setClassNamePrefix("reset");
		
		assertEquals("reset", StyleEditorPresenterUtils.getModuleClassNamePrefix(moduleMockup));
	}
}