package com.lorepo.iceditor.client.ui.widgets.content;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

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
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.iceditor.client.ui.page.ProxyWidget;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.LayoutDefinition;
import com.lorepo.icplayer.client.module.addon.AddonModel;

@GwtModule("com.lorepo.iceditor.Iceditor")
public class HeaderFooterModulesPositionTestCase extends GwtTest{
	PresentationWidget presentation = Mockito.mock(PresentationWidget.class);
	Content model = Mockito.mock(Content.class);
	Page page = new Page("page", "url");
	AddonModel module = new AddonModel();
	Element element = GWT.create(Element.class);
	
	Map<String,HashMap<String,ProxyWidget>> widgets = new HashMap<String, HashMap<String, ProxyWidget>>();
	IEditorServices editorServices = new IEditorServices() {
		
		@Override
		public Content getContent() {
			return model;
		}
	};
	
	@Before
	public void setUp() {		
		Mockito.when(presentation.calculatePosition("page", module)).thenCallRealMethod();
		Mockito.when(presentation.getEditorServices()).thenReturn(editorServices);
		Mockito.when(presentation.getElement()).thenReturn(element);
		Mockito.when(model.getPageById("page")).thenReturn(page);
		element.setPropertyInt("clientWidth", 400);
		element.setPropertyInt("clientHeight", 700);
		
		HashMap<String, ProxyWidget> map = new HashMap<String, ProxyWidget>();
		map.put("", null);
		widgets.put("page", map);
		
		Whitebox.setInternalState(presentation, "widgets", widgets);
		
		page.addSize("default", new Size("default", 400, 400));
		page.addModule(module);
		
		module.addSemiResponsiveDimensions("default", new ModuleDimensions(0, 100, 0, 100, 50, 50));
		LayoutDefinition layout = module.getResponsiveRelativeLayouts().get("default");
		layout.setHasLeft(false);
		layout.setHasRight(true);
		layout.setHasTop(false);
		layout.setHasBottom(true);
	}
	
	@Test
	public void moduleRelativeToBottomRight() {
		HashMap<String, Integer> result = presentation.calculatePosition("page", module);
		assertEquals((Integer)250, result.get("left"));
		assertEquals((Integer)300, result.get("right"));
		assertEquals((Integer)250, result.get("top"));
		assertEquals((Integer)300, result.get("bottom"));
		
	}
}
