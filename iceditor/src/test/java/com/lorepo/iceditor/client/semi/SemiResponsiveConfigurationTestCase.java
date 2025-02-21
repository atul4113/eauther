package com.lorepo.iceditor.client.semi;

import static org.junit.Assert.*;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SemiResponsiveConfigurationTestCase {
	SemiResponsiveConfigurationJava configuration = null;
	Set<PageLayout> layouts = null;
	
	private PageLayout createLayout(String id, String name, int threshold) {
		PageLayout layout = new PageLayout(id, name);
		layout.setThreshold(threshold);
		return layout;
	}
	
	@Before
	public void setUp() {
		layouts = new HashSet<PageLayout>();
		layouts.add(createLayout("ID1", "NAME1", 100));
		layouts.add(createLayout("ID2", "NAME2", 200));
		layouts.add(createLayout("ID3", "NAME3", 300));
		
		this.configuration = new SemiResponsiveConfigurationJava(this.layouts);
	}
	
	@Test
	public void GetSizeTest() {
		int expected = this.layouts.size();
		
		assertEquals(expected, this.configuration.length());
	}
	
	@Test
	public void GetThresholdTest() {
		assertEquals(100, this.configuration.getThreshold("ID1"));
		assertEquals(200, this.configuration.getThreshold("ID2"));
		assertEquals(300, this.configuration.getThreshold("ID3"));
	
		assertEquals(0, this.configuration.getThreshold("NonExistent"));
	}
	
	@Test
	public void GetNameTest() {
		assertEquals("NAME1", this.configuration.getName("ID1"));
		assertEquals("NAME2", this.configuration.getName("ID2"));
		assertEquals("NAME3", this.configuration.getName("ID3"));
		
		assertEquals(null, this.configuration.getName("NonExistent"));
	}
	
}
