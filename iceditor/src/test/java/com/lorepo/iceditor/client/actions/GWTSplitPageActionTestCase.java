package com.lorepo.iceditor.client.actions;

import static org.junit.Assert.assertEquals;

import java.util.HashMap;
import java.util.Map;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.reflect.Whitebox;

import com.google.gwt.core.shared.GWT;
import com.google.gwt.user.client.Element;
import com.googlecode.gwt.test.GwtModule;
import com.googlecode.gwt.test.GwtTest;
import com.lorepo.iceditor.client.actions.mockup.ActionServicesMockup;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.page.ProxyWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.xml.page.PageFactory;

@GwtModule("com.lorepo.iceditor.Iceditor")
public class GWTSplitPageActionTestCase extends GwtTest{
	ActionServicesMockup actionServices;
	Element element;
	SplitPageAction action;
	SplitPageAction actionSpy;
	AppFrame appFrame;
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
		actionServices = new ActionServicesMockup();
		action = new SplitPageAction(actionServices);
		actionSpy = Mockito.spy(action);
		appFrame = Mockito.mock(AppFrame.class);
		presentation = Mockito.mock(PresentationWidget.class);
		model = Mockito.mock(Content.class);
		element = GWT.create(Element.class);
		
		Mockito.doReturn(appFrame).when(actionSpy).getAppFrame();
		Mockito.doReturn(presentation).when(appFrame).getPresentation();
		Mockito.when(presentation.calculatePosition(Mockito.anyString(), Mockito.any(IModuleModel.class))).thenCallRealMethod();
		Mockito.when(presentation.getElement()).thenReturn(element);
		Mockito.when(model.getPageById(Mockito.anyString())).thenReturn(oldPage);
		Mockito.when(presentation.getEditorServices()).thenReturn(editorServices);
		
		oldPage = new Page("old", "old");
		
		Map<String,HashMap<String,ProxyWidget>> widgets = new HashMap<String, HashMap<String, ProxyWidget>>();
		HashMap<String, ProxyWidget> map = new HashMap<String, ProxyWidget>();
		map.put("", null);
		widgets.put(oldPage.getId(), map);
		Whitebox.setInternalState(presentation, "widgets", widgets);
	}
	
	@Test
	public void twoModules(){
		oldPage.addSize("default", new Size("default", 300, 600));
		
		element.setPropertyInt("clientWidth", 300);
		element.setPropertyInt("clientHeight", 600);
		
		AddonModel module1 = new AddonModel();
		AddonModel module2 = new AddonModel();
		module1.addSemiResponsiveDimensions("default", new ModuleDimensions(100, 0, 100, 0, 50, 50));
		module2.addSemiResponsiveDimensions("default", new ModuleDimensions(300, 0, 300, 0, 50, 50));
		oldPage.addModule(module1);
		oldPage.addModule(module2);
		
		Whitebox.setInternalState(actionSpy, "splitFraction", (float)200/(float)600);
		String newPageXML = actionSpy.getPageXML(oldPage);
		
		Page newPage = new Page("","");
		PageFactory pf = new PageFactory(newPage);
		pf.produce(newPageXML, "");
		
		assertEquals(200, oldPage.getHeight());
		assertEquals(400, newPage.getHeight());
		assertEquals(1, oldPage.getModules().size());
		assertEquals(1, newPage.getModules().size());
		assertEquals(100, oldPage.getModules().get(0).getTop());
		assertEquals(100, newPage.getModules().get(0).getTop());
	}
	
	@Test
	public void twoLayouts() {
		oldPage.addSize("a", new Size("a", 300, 500));
		oldPage.addSize("b", new Size("b", 300, 1000));
		
		oldPage.setSemiResponsiveLayoutID("a");
		
		Whitebox.setInternalState(actionSpy, "splitFraction", (float)300/(float)500);
		String newPageXML = actionSpy.getPageXML(oldPage);
		
		Page newPage = new Page("","");
		PageFactory pf = new PageFactory(newPage);
		pf.produce(newPageXML, "");
		
		oldPage.setSemiResponsiveLayoutID("a");
		newPage.setSemiResponsiveLayoutID("a");
		assertEquals(300, oldPage.getHeight());
		assertEquals(200, newPage.getHeight());
		
		oldPage.setSemiResponsiveLayoutID("b");
		newPage.setSemiResponsiveLayoutID("b");
		assertEquals(600, oldPage.getHeight());
		assertEquals(400, newPage.getHeight());
		
	}
	
}