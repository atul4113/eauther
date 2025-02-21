package com.lorepo.iceditor.client.actions;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.reflect.Whitebox;
import org.xml.sax.SAXException;

import com.google.gwt.core.shared.GWT;
import com.google.gwt.xml.client.Element;
import com.googlecode.gwt.test.GwtModule;
import com.googlecode.gwt.test.GwtTest;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.SortModulesTextToSpeechAction.ModuleWrapper;
import com.lorepo.iceditor.client.actions.mockup.ActionServicesMockup;
import com.lorepo.iceditor.client.actions.mockup.AppControllerMockup;
import com.lorepo.iceditor.client.controller.ActionServices;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.page.ProxyWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.mockup.xml.PageFactoryMockup;
import com.lorepo.icplayer.client.mockup.xml.XMLParserMockup;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.page.PageFactory;
import com.lorepo.icplayer.client.xml.page.parsers.PageParser_v1;

@GwtModule("com.lorepo.iceditor.Iceditor")
public class SortModulesTextToSpeechActionTestCase extends GwtTest{
	ActionServices actionServices;
	ActionFactory actionFactory;
	Element element;
	SortModulesTextToSpeechAction action;
	SortModulesTextToSpeechAction actionSpy;
	AbstractAction sortAction;
	AppFrame appFrame;
	AppController appController;
	PresentationWidget presentation;
	Page oldPage;
	Content model;
	
	IEditorServices editorServices = new IEditorServices() {
		
		@Override
		public Content getContent() {
			return model;
		}
	};
	
	@Before
	public void setUp() {
		actionServices = Mockito.mock(ActionServices.class);
		model = Mockito.mock(Content.class);
		appController = Mockito.mock(AppController.class);
		action = new SortModulesTextToSpeechAction(appController);
		actionSpy = Mockito.spy(action);
		appFrame = Mockito.mock(AppFrame.class);
		presentation = Mockito.mock(PresentationWidget.class);
		actionFactory = Mockito.mock(ActionFactory.class);
		sortAction = Mockito.mock(AbstractAction.class);
		
		Mockito.doReturn(appFrame).when(actionSpy).getAppFrame();
		Mockito.doReturn(presentation).when(appFrame).getPresentation();
		Mockito.when(presentation.calculatePosition(Mockito.anyString(), Mockito.any(IModuleModel.class))).thenCallRealMethod();
		Mockito.when(appController.getActionServices()).thenReturn(actionServices);
		Mockito.when(appController.getActionFactory()).thenReturn(actionFactory);
		Mockito.when(actionServices.getModel()).thenReturn(model);
		Mockito.when(actionFactory.getAction(ActionType.sortModulesTextToSpeech)).thenReturn(sortAction);
	}
	
	@Test
	public void sortModulesInTextToSpeech() {
		Page page = new Page("AddonPage", "");
		loadPage("testdata/page.xml", page);
		
		action.execute(page);
	
		List<String> after = getTTSConfiguration(page);
		
		assertEquals(4, after.size());
		assertEquals("Connection1", after.get(0));
		assertEquals("Text1", after.get(1));
		assertEquals("Image2", after.get(2));
		assertEquals("Image1", after.get(3));
	}
	
	@Test
	public void sortModulesInTextToSpeechRightToLeft() {
		Mockito.when(model.getMetadataValue("sortRightToLeft")).thenReturn("True");
		Page page = new Page("AddonPage", "");
		loadPage("testdata/page.xml", page);
		
		action.execute(page);
	
		List<String> after = getTTSConfiguration(page);
		
		assertEquals(4, after.size());
		assertEquals("Connection1", after.get(0));
		assertEquals("Text1", after.get(1));
		assertEquals("Image1", after.get(2));
		assertEquals("Image2", after.get(3));
	}
	
	private void loadPage(String xmlFile, Page page) {
		InputStream inputStream = getClass().getResourceAsStream(xmlFile);
		try {
			XMLParserMockup xmlParser = new XMLParserMockup();
			Element element = xmlParser.parser(inputStream);
			PageParser_v1 parser = new PageParser_v1();
			parser.setPage(page);
			page = (Page) parser.parse(element);
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private List<String> getTTSConfiguration(Page page){
		List<String> result = new ArrayList<String>();
		
		ModuleList modules = page.getModules();
		IModuleModel ttsModel = modules.getModuleById("Text_To_Speech1");
		
		if (ttsModel == null) {
			return result;
		}
		
		IProperty configuration = null;
		for(int i = 0; i < ttsModel.getPropertyCount(); i++){
			if(ttsModel.getProperty(i).getName().equals("configuration")){
				configuration = ttsModel.getProperty(i);
				break;
			}
		}
		if (configuration == null){
			return result;
		}
		
		IListProperty configurationList = null;
		if(configuration instanceof IListProperty){
			configurationList = (IListProperty) configuration;
		} else return result;
		
		for(int j=0; j<configurationList.getChildrenCount();j++){
			IPropertyProvider child = configurationList.getChild(j);
			String id = "";
			for(int i = 0; i < child.getPropertyCount(); i++){
				IProperty field = child.getProperty(i);
				if(field.getName().equals("ID")){
					id = field.getValue();
				}
			}
			result.add(id);
		}
		return result;
		
	}
	
}