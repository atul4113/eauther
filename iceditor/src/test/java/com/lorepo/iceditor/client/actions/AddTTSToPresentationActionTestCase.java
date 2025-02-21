package com.lorepo.iceditor.client.actions;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.tools.ant.filters.StringInputStream;
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
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.mockup.xml.PageFactoryMockup;
import com.lorepo.icplayer.client.mockup.xml.XMLParserMockup;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.page.PageFactory;
import com.lorepo.icplayer.client.xml.page.parsers.PageParser_v1;

@GwtModule("com.lorepo.iceditor.Iceditor")
public class AddTTSToPresentationActionTestCase extends GwtTest{
	ActionServices actionServices;
	ActionFactory actionFactory;
	Element element;
	AddTTSToPresentationAction action;
	AddTTSToPresentationAction actionSpy;
	AbstractAction sortAction;
	AddAllTextToSpeechAction addTTSAction;
	AddAllTextToSpeechAction addTTSActionSpy;
	AppFrame appFrame;
	AppController appController;
	PresentationWidget presentation;
	Page oldPage;
	Content model;
	List<Page> pages;
	ModalsWidget modals;
	ModulesWidget modules;
	AddonDescriptor ttsDescriptor;
	
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
		action = new AddTTSToPresentationAction(appController);
		actionSpy = Mockito.spy(action);
		appFrame = Mockito.mock(AppFrame.class);
		presentation = Mockito.mock(PresentationWidget.class);
		actionFactory = Mockito.mock(ActionFactory.class);
		sortAction = Mockito.mock(AbstractAction.class);
		addTTSAction = Mockito.mock(AddAllTextToSpeechAction.class);
		modals = Mockito.mock(ModalsWidget.class);
		modules = Mockito.mock(ModulesWidget.class);
		ttsDescriptor = initDescriptor();
		
		Mockito.doReturn(presentation).when(appFrame).getPresentation();
		Mockito.when(presentation.calculatePosition(Mockito.anyString(), Mockito.any(IModuleModel.class))).thenCallRealMethod();
		Mockito.when(appController.getActionServices()).thenReturn(actionServices);
		Mockito.when(appController.getActionFactory()).thenReturn(actionFactory);
		Mockito.when(appController.getAppFrame()).thenReturn(appFrame);
		Mockito.when(actionServices.getModel()).thenReturn(model);
		Mockito.when(actionServices.getAppController()).thenReturn(appController);
		Mockito.when(actionFactory.getAction(ActionType.sortModulesTextToSpeech)).thenReturn(sortAction);
		Mockito.when(actionFactory.getAction(ActionType.addAllTextToSpeech)).thenReturn(addTTSAction);
		Mockito.when(appFrame.getModals()).thenReturn(modals);
		Mockito.when(appFrame.getModules()).thenReturn(modules);
		Mockito.when(model.getAddonDescriptor("Text_To_Speech")).thenReturn(ttsDescriptor);
		Mockito.when(model.addonIsLoaded("Text_To_Speech")).thenReturn(true);
	}
	
	@Test
	public void addMissingTextToSpeech() {
		pages = new ArrayList<Page>();
		Page page = new Page("AddonPage", "");
		loadPage("testdata/page.xml", page);
		pages.add(page);
		Page pageWithoutTTS = new Page("AddonPage", "");
		loadPage("testdata/pageWithoutTTS.xml", pageWithoutTTS);
		pages.add(pageWithoutTTS);
		Mockito.when(model.getAllPages()).thenReturn(pages);
		
		action.execute();

		boolean hasTTS = false;
		List<String> moduleIDs = pageWithoutTTS.getModulesList();
		for (String id: moduleIDs) {
			if (id.equals("Text_To_Speech1")) {
				hasTTS = true;
				break;
			}
		}
		assertTrue(hasTTS);
		Mockito.verify(addTTSAction).execute(pageWithoutTTS);
		
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
	
	private AddonDescriptor initDescriptor() {
		try{
			InputStream inputStream = getClass().getResourceAsStream("testdata/ttsDescriptor.xml");
			XMLParserMockup xmlParser = new XMLParserMockup();
			Element element = xmlParser.parser(inputStream);
			
			AddonDescriptor descriptor = new AddonDescriptor("Text_To_Speech", "");
			descriptor.load(element, "");
			
			return descriptor;
		} catch (Exception e) {
			return null;
		}
	}
	
}