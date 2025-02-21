package com.lorepo.iceditor.client.controller;

import static org.junit.Assert.*;

import org.junit.Before;
import org.junit.Test;

import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.choice.ChoiceModel;
import com.lorepo.icplayer.client.module.ordering.OrderingModule;
import com.lorepo.icplayer.client.module.report.ReportModule;
import com.lorepo.icplayer.client.module.sourcelist.SourceListModule;
import com.lorepo.icplayer.client.module.text.TextModel;

public class GroupModulesTestCase {
	SelectionController selectionController;
	Group group1;
	Group group2;
	IModuleModel module1;
	IModuleModel module2;
	IModuleModel module3;
	IModuleModel module4;
	IModuleModel module5;
	IModuleModel module6;
	
	@Before
	public void setup() {
		selectionController = new SelectionController(null);
		group1 = new Group();
		group2 = new Group();
		module1 = new ChoiceModel();
		module2 = new TextModel();
		module3 = new OrderingModule();
		module4 = new TextModel();
		module5 = new ReportModule();
		module6 = new SourceListModule();
	}
	
	@Test
	public void addingOneGroup() {
		group1.add(module1);
		group1.add(module2);
		group1.add(module3);
		
		selectionController.addGroupedModules("somePageID", group1);
		
		assertEquals(group1, selectionController.getPageGroups("somePageID").get(0));
	}
	
	@Test
	public void addingMultipleGroupsOnSamePage() {
		
		group1.add(module1);
		group1.add(module2);
		group1.add(module3);
		group2.add(module4);
		group2.add(module5);
		group2.add(module6);
		
		selectionController.addGroupedModules("somePageID", group1);
		selectionController.addGroupedModules("somePageID", group2);
		
		assertEquals(group1, selectionController.getPageGroups("somePageID").get(0));
		assertEquals(group2, selectionController.getPageGroups("somePageID").get(1));
	}
	
	@Test
	public void addingMultipleGroupsOnMultiplePages() {
		
		group1.add(module1);
		group1.add(module2);
		group1.add(module3);
		group2.add(module4);
		group2.add(module5);
		group2.add(module6);
		
		selectionController.addGroupedModules("somePageID", group1);
		selectionController.addGroupedModules("somePageID2", group2);
		
		assertEquals(1, selectionController.getPageGroups("somePageID").size());
		assertEquals(group1, selectionController.getPageGroups("somePageID").get(0));
		assertEquals(1, selectionController.getPageGroups("somePageID2").size());
		assertEquals(group2, selectionController.getPageGroups("somePageID2").get(0));
	}
	
	@Test
	public void addingSameGroupTwiceOnSamePage() {

		group1.add(module1);
		group1.add(module2);
		group1.add(module3);
		
		selectionController.addGroupedModules("somePageID", group1);
		selectionController.addGroupedModules("somePageID", group1);
		
		assertEquals(group1, selectionController.getPageGroups("somePageID").get(0));
		assertEquals(1, selectionController.getPageGroups("somePageID").size());
	}
	
	
	
	@Test
	public void removingLastGroupOnPage() {
		
		group1.add(module1);
		group1.add(module2);
		
		selectionController.addGroupedModules("somePageID", group1);
		
		assertEquals(1, selectionController.getPageGroups("somePageID").size());
		
		selectionController.removeGroup("somePageID", group1.iterator());
		
		assertEquals(0, selectionController.getPageGroups("somePageID").size());
	}
	
	@Test
	public void removingOneOfTheGroups() {
		
		group1.add(module1);
		group1.add(module2);
		group2.add(module4);
		group2.add(module5);
		
		selectionController.addGroupedModules("somePageID", group1);
		selectionController.addGroupedModules("somePageID", group2);
		
		assertEquals(2, selectionController.getPageGroups("somePageID").size());
		
		selectionController.removeGroup("somePageID", group1.iterator());
		
		assertEquals(1, selectionController.getPageGroups("somePageID").size());
		assertEquals(group2, selectionController.getPageGroups("somePageID").get(0));
	} 
	
	@Test
	public void removingGroupFromPageWhenItExistsOnDifferentOne() {
		group1.add(module1);
		group1.add(module2);
		
		selectionController.addGroupedModules("somePageID", group1);
		selectionController.addGroupedModules("somePageID2", group1);
		
		selectionController.removeGroup("somePageID", group1.iterator());
		
		assertEquals(0, selectionController.getPageGroups("somePageID").size());
		assertEquals(1, selectionController.getPageGroups("somePageID2").size());
		assertEquals(group1, selectionController.getPageGroups("somePageID2").get(0));
	}
	
	@Test
	public void removingGroupThatDoesntExists() {
		
		group1.add(module1);
		group1.add(module2);
		
		selectionController.addGroupedModules("somePageID", group1);

		group2.add(module3);
		group2.add(module2);
		
		selectionController.addGroupedModules("somePageID2", group2);
		
		selectionController.removeGroup("somePageID", group1.iterator());
		
		assertEquals(0, selectionController.getPageGroups("somePageID").size());
		assertEquals(1, selectionController.getPageGroups("somePageID2").size());
		assertEquals(group2, selectionController.getPageGroups("somePageID2").get(0));
	}
}
