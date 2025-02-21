package com.lorepo.iceditor.client.semi;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import com.lorepo.icplayer.client.dimensions.ModuleDimensions;
import com.lorepo.icplayer.client.model.ModuleList;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.model.layout.Size;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.BasicModuleModel;
import com.lorepo.icplayer.client.module.LayoutDefinition;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.SemiResponsiveLayouts;

public class TranslateImportedPageLayoutsTaskTestCase {
	
	private SemiResponsiveConfiguration importedPageConfiguration;
	private Page pageToSync = new Page("Page", "localhost");
	private Set<PageLayout> actualConfiguration = new HashSet<PageLayout>();
	
	private HashMap<String, Size> expectedSizes = new HashMap<String, Size>();
	private ModuleList expectedModuleList = this.createModuleList("default", "mobile", "desktop");

	@Before
	public void setUp() {
		this.initImportedPageConfiguration();
		this.initImportedPage();
		this.initActualConfiguration();
		this.initExpectedSizes();
	}
	
	private void initExpectedSizes() {
		expectedSizes.put("default", new Size("default", 400, 800));
		expectedSizes.put("desktop", new Size("desktop", 800, 800));
		expectedSizes.put("mobile", new Size("mobile", 1200, 1200));
	}


	private void initImportedPageConfiguration() {
		HashMap<String, PageLayout> configuration = new HashMap<String, PageLayout>();
		PageLayout p1 = new PageLayout("layoutdefault", "layoutdefault", 800);
		p1.setIsDefault(true);
		PageLayout p2 = new PageLayout("b", "b", 400);
		PageLayout p3 = new PageLayout("c", "c", 1200);
		
		configuration.put(p1.getID(), p1);
		configuration.put(p2.getID(), p2);
		configuration.put(p3.getID(), p3);
		
		importedPageConfiguration = new SemiResponsiveConfigurationMock(configuration);
	}
	
	private void initActualConfiguration() {
		PageLayout defaultLayout = new PageLayout("default", "default", 800);
		defaultLayout.setIsDefault(true);
		
		PageLayout mobileLayout = new PageLayout("mobile", "mobile", 400);
		PageLayout desktopLayout = new PageLayout("desktop", "desktop", 1200);
		PageLayout customLayout = new PageLayout("custom", "custom", 2200);
		
		this.actualConfiguration.add(defaultLayout);
		this.actualConfiguration.add(mobileLayout);
		this.actualConfiguration.add(desktopLayout);
		this.actualConfiguration.add(customLayout);
	}

	private void initImportedPage() {
		Size defaultSize = new Size("layoutdefault", 400, 800);
		Size bSize = new Size("b", 1200, 1200);
		Size cSize = new Size("c", 800, 800);
		
		this.pageToSync.addSize("layoutdefault", defaultSize);
		this.pageToSync.addSize("b", bSize);
		this.pageToSync.addSize("c", cSize);
		

		for (IModuleModel module : this.createModuleList("layoutdefault", "b", "c")) {
			this.pageToSync.addModule(module);	
		}
	}
	
	private ModuleList createModuleList(String defaultLayout, String layoutB, String layoutC) {
		AddonModel module1 = new AddonModel();
		module1.setIsVisible(true);
		module1.setRelativeLayout(defaultLayout, new LayoutDefinition());
		module1.addSemiResponsiveDimensions(defaultLayout, new ModuleDimensions(100, 100, 100, 100, 100, 100));
		module1.setIsLocked(defaultLayout, true);
		module1.setIsVisibleInEditor(defaultLayout, true);
		
		module1.setRelativeLayout(layoutB, new LayoutDefinition());
		module1.addSemiResponsiveDimensions(layoutB, new ModuleDimensions(100, 100, 100, 100, 100, 100));
		module1.setIsLocked(layoutB, false);
		module1.setIsVisibleInEditor(layoutB, false);
		
		AddonModel module2 = new AddonModel();
		module1.setIsVisible(true);
		module2.setRelativeLayout(defaultLayout, new LayoutDefinition());
		module2.addSemiResponsiveDimensions(defaultLayout, new ModuleDimensions(200, 200, 200, 200, 200, 200));
		module2.setIsLocked(defaultLayout, true);
		module2.setIsVisibleInEditor(defaultLayout, true);
		
		module2.setRelativeLayout(layoutC, new LayoutDefinition());
		module2.addSemiResponsiveDimensions(layoutC, new ModuleDimensions(200, 200, 200, 200, 200, 200));
		module2.setIsLocked(layoutC, false);
		module2.setIsVisibleInEditor(layoutC, false);
		
		AddonModel module3 = new AddonModel();
		module1.setIsVisible(false);
		module3.setRelativeLayout(defaultLayout, new LayoutDefinition());
		module3.addSemiResponsiveDimensions(defaultLayout, new ModuleDimensions(300, 300, 300, 300, 300, 300));
		module3.setIsLocked(defaultLayout, true);
		module3.setIsVisibleInEditor(defaultLayout, true);
		
		module3.setRelativeLayout(layoutB, new LayoutDefinition());
		module3.addSemiResponsiveDimensions(layoutB, new ModuleDimensions(400, 400, 400, 400, 400, 400));
		module3.setIsLocked(layoutB, false);
		module3.setIsVisibleInEditor(layoutB, true);
		
		module3.setRelativeLayout(layoutC, new LayoutDefinition());
		module3.addSemiResponsiveDimensions(layoutC, new ModuleDimensions(300, 300, 300, 300, 300, 300));
		module3.setIsLocked(layoutC, false);
		module3.setIsVisibleInEditor(layoutC, false);
		
		ModuleList result = new ModuleList();
		result.add(module1);
		result.add(module2);
		result.add(module3);
		return result;
	}
	
	@Test
	public void translatePageSizes() {
		TranslateImportedPageLayoutsTask task = new TranslateImportedPageLayoutsTask();
		
		Page translatedPage = task.execute(this.importedPageConfiguration, this.pageToSync, actualConfiguration);
		HashMap<String, Size> result = translatedPage.getSizes();		
		
		assertEquals(this.expectedSizes.size(), result.size());
		assertEquals(this.expectedSizes, result);
	}
	
	@Test
	public void translateModules() {
		TranslateImportedPageLayoutsTask task = new TranslateImportedPageLayoutsTask();
		
		Page translatedPage = task.execute(this.importedPageConfiguration, this.pageToSync, actualConfiguration);
		ModuleList result = translatedPage.getModules();
		
		assertEquals(this.expectedModuleList.size(), result.size());
		
		for(int i = 0; i < this.expectedModuleList.size(); i++) {
			SemiResponsiveLayouts expectedModule = this.expectedModuleList.get(i);
			SemiResponsiveLayouts resultModule = result.get(i);
			
			assertTrue(expectedModule instanceof BasicModuleModel);
			assertTrue(resultModule instanceof BasicModuleModel);
			if(expectedModule instanceof BasicModuleModel && resultModule instanceof BasicModuleModel) {
				BasicModuleModel expectedBasicModule = (BasicModuleModel) expectedModule;
				BasicModuleModel resultBasicModule = (BasicModuleModel) resultModule;
				assertEquals(expectedBasicModule.isVisible(), resultBasicModule.isVisible());
			}
			
			assertEquals(expectedModule.getResponsiveLayouts(), resultModule.getResponsiveLayouts());
			assertEquals(expectedModule.getResponsiveLocked(), resultModule.getResponsiveLocked());
			assertEquals(expectedModule.getResponsiveVisibilityInEditor(), resultModule.getResponsiveVisibilityInEditor());
		}
	}
}
