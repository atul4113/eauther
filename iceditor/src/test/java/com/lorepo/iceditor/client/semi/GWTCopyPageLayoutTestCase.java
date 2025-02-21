package com.lorepo.iceditor.client.semi;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Random;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;

import org.custommonkey.xmlunit.XMLUnit;
import org.junit.Before;
import org.junit.Test;
import org.xml.sax.SAXException;

import com.googlecode.gwt.test.GwtModule;
import com.googlecode.gwt.test.GwtTest;
import com.lorepo.iceditor.client.semi.responsive.CopyPageLayoutTask;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.mockup.xml.PageFactoryMockup;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.semi.responsive.SemiResponsiveStyles;


@GwtModule("com.lorepo.iceditor.Iceditor")
public class GWTCopyPageLayoutTestCase extends GwtTest {
	
	private Page loadFromString(Page page, String xml) {
		return new PageFactoryMockup(page).loadFromString(xml);
	}

	@Before
	public void setUp() throws ParserConfigurationException, SAXException, IOException, TransformerException {
		XMLUnit.setIgnoreWhitespace(true);
		XMLUnit.setIgnoreComments(true);
		XMLUnit.setIgnoreDiffBetweenTextAndCDATA(true);
		XMLUnit.setNormalizeWhitespace(true);
		XMLUnit.setIgnoreAttributeOrder(true);
	}
	
	@Test
	public void pageXML() throws SAXException, IOException {
		Page page = new Page("page","");
		
		int numberOfModules = 2;
		
		String[] classes = {"class_1", "class_2", "class_3"};
		String[] inlines = {"background: red;", "background: blue;"};
		
		page.getSizes().put("a", new Size(null, 1200, 1600));
		page.getSemiResponsiveStyles().setInlineStyle("a", "page inline style");
		page.getSemiResponsiveStyles().setStyleClass("a", "page_style_class");
		
		ArrayList<AddonModel> modules = new ArrayList<AddonModel>();
		
		for (int i = 0; i < numberOfModules; i++) {
			AddonModel module = new AddonModel();
			module.getSemiResponsiveStyles().setStyleClass("a", classes[i%classes.length]);
			module.getSemiResponsiveStyles().setInlineStyle("a", inlines[i%inlines.length]);
			
			module.setSemiResponsiveLayoutID("a");
			module.copyConfiguration("default");
			module.getResponsiveLayouts().put("a", new ModuleDimensions(300, 300, 100, 100, 50, 50));

			module.setSemiResponsiveLayoutID("b");
			modules.add(module);
			page.getModules().add(module);
		}
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(page, "a", "b");
		
		String xml = page.toXML();
		Page loadedPage = this.loadFromString(new Page("id", "path"), xml);
		
		ModuleList loadedModules = loadedPage.getModules();
		
		assertEquals(page.getSizes().get("a").getWidth(), loadedPage.getSizes().get("b").getWidth());
		assertEquals(page.getSizes().get("a").getHeight(), loadedPage.getSizes().get("b").getHeight());
		
		SemiResponsiveStyles pageStyles = page.getSemiResponsiveStyles();
		SemiResponsiveStyles loadedPageStyles = loadedPage.getSemiResponsiveStyles();
		
		assertEquals(pageStyles.getInlineStyle("a", "a"), loadedPageStyles.getInlineStyle("b", "b"));
		assertEquals(pageStyles.getStyleClass("a", "a"), loadedPageStyles.getStyleClass("b", "b"));
		
		for (int i = 0; i < numberOfModules; i++){
			HashMap<String, ModuleDimensions> moduleLayouts = modules.get(i).getResponsiveLayouts();
			HashMap<String, ModuleDimensions> loadedModuleLayouts = loadedModules.get(i).getResponsiveLayouts();
			
			assertEquals(moduleLayouts.get("a").bottom, loadedModuleLayouts.get("a").bottom);
			assertEquals(moduleLayouts.get("a").height, loadedModuleLayouts.get("b").height);
			assertEquals(moduleLayouts.get("a").left, loadedModuleLayouts.get("b").left);
			assertEquals(moduleLayouts.get("a").right, loadedModuleLayouts.get("b").right);
			assertEquals(moduleLayouts.get("a").top, loadedModuleLayouts.get("b").top);
			assertEquals(moduleLayouts.get("a").width, loadedModuleLayouts.get("b").width);
			
			SemiResponsiveStyles moduleStyles = modules.get(i).getSemiResponsiveStyles();
			SemiResponsiveStyles loadedModuleStyles = modules.get(i).getSemiResponsiveStyles();
			
			assertEquals(moduleStyles.getInlineStyle("a", "a"), loadedModuleStyles.getInlineStyle("b", "b"));
			assertEquals(moduleStyles.getStyleClass("a", "a"), loadedModuleStyles.getStyleClass("b", "b"));
		}
	}
}