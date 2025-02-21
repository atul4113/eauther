package com.lorepo.iceditor.client.actions;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class InsertButtonActionTestCase {

	@Test
	public void getProperButtonName() {
		
		assertEquals("Reset", InsertButtonAction.getProperButtonName("reset"));
		assertEquals("ClosePopup", InsertButtonAction.getProperButtonName("cancel"));
		assertEquals("Text", InsertButtonAction.getProperButtonName("Text"));
	}
	
}