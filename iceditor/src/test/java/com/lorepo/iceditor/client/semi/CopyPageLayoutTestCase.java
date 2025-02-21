package com.lorepo.iceditor.client.semi;

import static org.junit.Assert.*;

import java.io.IOException;
import java.util.ArrayList;

import org.junit.Before;
import org.junit.Test;
import org.xml.sax.SAXException;

import com.googlecode.gwt.test.GwtModule;
import com.lorepo.iceditor.client.semi.responsive.CopyPageLayoutTask;
import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.semi.responsive.SemiResponsiveStyles;


@GwtModule(value = "")
public class CopyPageLayoutTestCase {
	Content model = new Content();
	Page page = new Page("Page", "loclahost");
	PageLayout layoutA = new PageLayout("a", "a", 400);
	PageLayout layoutB = new PageLayout("b", "b", 1200);
	
	@Before
	public void setUp() {
		this.model.addLayout(layoutA);
		this.model.addLayout(layoutB);
		
		Size pageSize = new Size("a", 200, 300);
		page.getSizes().put("a", pageSize);
	}
	
	@Test
	public void pageSize() {
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");
		
		assertEquals(200, page.getSizes().get("b").getWidth());
		assertEquals(300, page.getSizes().get("b").getHeight());
	}
	
	@Test
	public void pageInlineStyle() {
		String inlineStyle = "background: red;";
		SemiResponsiveStyles styles = page.getSemiResponsiveStyles();
		styles.setInlineStyle("a", inlineStyle);
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");

		assertEquals(inlineStyle, styles.getInlineStyle("b", "b"));
		assertEquals(styles.getInlineStyle("a", "a"), styles.getInlineStyle("b", "b"));
	}
	
	@Test
	public void pageStyleClass() {
		String styleClass = "sample_class";
		SemiResponsiveStyles styles = page.getSemiResponsiveStyles();
		styles.setStyleClass("a", styleClass);
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");

		assertEquals(styleClass, styles.getStyleClass("b", "b"));
		assertEquals(styles.getStyleClass("a", "a"), styles.getStyleClass("b", "b"));
	}

	@Test
	public void moduleInlineStyle() {
		String inlineStyle = "background: red;";
		AddonModel module = new AddonModel();
		this.page.addModule(module);
		
		SemiResponsiveStyles styles = module.getSemiResponsiveStyles();
		styles.setInlineStyle("a", inlineStyle);
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");

		assertEquals(inlineStyle, styles.getInlineStyle("b", "b"));
		assertEquals(styles.getInlineStyle("a", "a"), styles.getInlineStyle("b", "b"));
		
	}
	
	@Test
	public void moduleStyleClass() {
		String styleClass = "sample_class";
		AddonModel module = new AddonModel();
		this.page.addModule(module);
		
		SemiResponsiveStyles styles = module.getSemiResponsiveStyles();
		styles.setStyleClass("a", styleClass);
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");

		assertEquals(styleClass, styles.getStyleClass("b", "b"));
		assertEquals(styles.getStyleClass("a", "a"), styles.getStyleClass("b", "b"));		
	}
	
	@Test
	public void moduleDimensions() {
		AddonModel module = new AddonModel();
		this.page.addModule(module);
		
		module.getResponsiveLayouts().put("b", new ModuleDimensions());
		module.getResponsiveLayouts().put("a", new ModuleDimensions(10, 20, 30, 40, 50, 60));
		module.setSemiResponsiveLayoutID("b");
		
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");
		
		assertEquals(module.getResponsiveLayouts().get("b").left, 10);
	}
	
	@Test
	public void multipleModules() throws SAXException, IOException {
		int numberOfModules = 30;
		
		String[] classes = {"class_1", "class_2", "class_3"};
		String[] inlines = {"inline_1", "inline_2"};
		
		page.getSemiResponsiveStyles().setInlineStyle("a", "page inline style");
		page.getSemiResponsiveStyles().setStyleClass("a", "page_style_class");
		
		ArrayList<AddonModel> modules = new ArrayList<AddonModel>();
		for (int i = 0; i < numberOfModules; i++) {
			AddonModel module = new AddonModel();
			module.getSemiResponsiveStyles().setStyleClass("a", classes[i%classes.length]);
			module.getSemiResponsiveStyles().setInlineStyle("a", inlines[i%inlines.length]);
			
			module.getResponsiveLayouts().put("a", new ModuleDimensions(300, 300, 100, 100, 50, 50));
			module.setSemiResponsiveLayoutID("b");
			
		}
		CopyPageLayoutTask task = new CopyPageLayoutTask();
		task.execute(this.page, "a", "b");
		
		assertEquals("page inline style", page.getSemiResponsiveStyles().getInlineStyle("b", "b"));
		assertEquals("page_style_class", page.getSemiResponsiveStyles().getStyleClass("b", "b"));
		
		for (AddonModel module : modules) {
			assertEquals(module.getResponsiveLayouts().get("a").bottom, module.getResponsiveLayouts().get("b").bottom);
			assertEquals(module.getResponsiveLayouts().get("a").height, module.getResponsiveLayouts().get("b").height);
			assertEquals(module.getResponsiveLayouts().get("a").left, module.getResponsiveLayouts().get("b").left);
			assertEquals(module.getResponsiveLayouts().get("a").right, module.getResponsiveLayouts().get("b").right);
			assertEquals(module.getResponsiveLayouts().get("a").top, module.getResponsiveLayouts().get("b").top);
			assertEquals(module.getResponsiveLayouts().get("a").width, module.getResponsiveLayouts().get("b").width);
			
			SemiResponsiveStyles styles = module.getSemiResponsiveStyles();
			assertEquals(styles.getInlineStyle("a",  "a"), styles.getInlineStyle("b", "b"));
			assertEquals(styles.getStyleClass("a", "a"), styles.getStyleClass("b", "b"));
		}
	}
}
	