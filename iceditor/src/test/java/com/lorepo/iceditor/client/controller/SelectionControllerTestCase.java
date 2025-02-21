package com.lorepo.iceditor.client.controller;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;

import com.google.gwt.view.client.MultiSelectionModel;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.image.ImageModule;
import com.lorepo.icplayer.client.module.text.TextModel;

public class SelectionControllerTestCase {
	private AppController mockedAppController;
	private SelectionController mockedSelectionController;
	private List<Group> groupedModules = new ArrayList<Group>();
	private IModuleModel selectedTextModule = new TextModel();
	private IModuleModel selectedImageModule = new ImageModule();
	private MultiSelectionModel<IModuleModel> mockedSelectionModel;
	private HashSet<IModuleModel> selectedSet;
	private Group selectedGroup;

	@SuppressWarnings({ "unchecked", "serial" })
	@Before
	public void setUp () {		
		mockedSelectionController = Mockito.mock(SelectionController.class);
		
		mockedAppController = Mockito.mock(AppController.class);
		Mockito.when(mockedAppController.getCurrentPage()).thenReturn(Mockito.mock(Page.class));
		Mockito.when(mockedAppController.getCurrentPage().getId()).thenReturn("someId");
		Mockito.when(mockedAppController.getSelectionController()).thenReturn(mockedSelectionController);
				
		selectedSet = new HashSet<IModuleModel>() {{
			add(selectedTextModule);
		}};
		
		selectedGroup = new Group();
		selectedGroup.addAll(selectedSet);
		
		mockedSelectionModel = Mockito.mock(MultiSelectionModel.class);
		Mockito.when(mockedSelectionModel.getSelectedSet()).thenReturn(selectedSet);
	}
	
	@Test
	public void groupIsNull() {
		groupedModules = null;
		Mockito.when(mockedAppController.getSelectionController().getPageGroups("someId")).thenReturn(groupedModules);
				
		assertFalse(SelectionControllerUtils.isGroupInSelectedModules(selectedGroup, mockedAppController));
	}
	
	@Test
	public void groupIsEmpty() {
		Mockito.when(mockedAppController.getSelectionController().getPageGroups("someId")).thenReturn(groupedModules);
		
		assertTrue(groupedModules.isEmpty());
		assertFalse(SelectionControllerUtils.isGroupInSelectedModules(selectedGroup, mockedAppController));
	}
	
	@SuppressWarnings("serial")
	@Test
	public void groupContainsModule() {
		Group group = new Group() {{
			add(selectedTextModule);
		}};

		groupedModules.add(group);
		groupedModules.add(new Group());
		groupedModules.add(new Group());

		Mockito.when(mockedAppController.getSelectionController().getPageGroups("someId")).thenReturn(groupedModules);
		
		assertTrue(SelectionControllerUtils.isGroupInSelectedModules(selectedGroup, mockedAppController));
	}
	
	@Test
	public void groupDoesntContainModule() {
		groupedModules.add(new Group());
		groupedModules.add(new Group());
		groupedModules.add(new Group());
		
		Mockito.when(mockedAppController.getSelectionController().getPageGroups("someId")).thenReturn(groupedModules);
		
		assertFalse(groupedModules.isEmpty());
		assertFalse(SelectionControllerUtils.isGroupInSelectedModules(selectedGroup, mockedAppController));
	}
	
	@Test
	public void findGroupWhenItDoesntExist() {
		SelectionController selectionController = new SelectionController(null);
		IModuleModel newGroup = new ImageModule();
		
		assertEquals(null, selectionController.findGroup(newGroup));
	}
	
	@SuppressWarnings("serial")
	@Test
	public void findGroupWhenItExists() {
		SelectionController selectionController = new SelectionController(null);

		Group group1 = new Group() {{
			add(selectedTextModule);
		}};
		
		Group group2 = new Group() {{
			add(selectedImageModule);
		}};
		
		groupedModules.add(group1);
		groupedModules.add(group2);
		
		Page page = new Page("someId", "");
		selectionController.setContentNode(page);
		selectionController.addGroupedModules(page.getId(), group1);
		selectionController.addGroupedModules(page.getId(), group2);
		
		assertEquals(group2, selectionController.findGroup(selectedImageModule));
	}
}
