package com.lorepo.iceditor.client.controller.addons;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;

import org.junit.Test;
import org.xml.sax.SAXException;

import com.google.gwt.xml.client.Element;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icplayer.client.mockup.xml.XMLParserMockup;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonProperty;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;

public class UpdatePageAddonsTestCase {

	private final String ADDON_ID = "Addon1";
	
	@Test
	public void updateEmpty() throws IOException {
		
		AddonDescriptor desc1 = new AddonDescriptor(ADDON_ID, "string");
		desc1.addProperty(new AddonProperty("abc", "ABC", "string"));
		HashMap<String, AddonDescriptor> descriptors = new HashMap<String, AddonDescriptor>();
		descriptors.put(ADDON_ID, desc1);
		AddonModel addon = new AddonModel();
		addon.setAddonId(ADDON_ID);
		Page page = new Page("Page 1", "");
		page.getModules().add(addon);
		
		UpdatePageAddons updater = new UpdatePageAddons(descriptors);
		updater.update(page);

		assertEquals(11, addon.getPropertyCount());
		assertEquals("abc", addon.getProperty(10).getName());
		
		desc1.addProperty(new AddonProperty("efg", "EFG", "string"));
		updater.update(page);
		assertEquals(12, addon.getPropertyCount());
		assertEquals("efg", addon.getProperty(11).getName());
		assertEquals("EFG", addon.getProperty(11).getDisplayName());
	}

	
	@Test
	public void updateList() throws IOException, SAXException {
		
		AddonDescriptor descriptor = loadDescriptor();

		HashMap<String, AddonDescriptor> descriptors = new HashMap<String, AddonDescriptor>();
		descriptors.put(ADDON_ID, descriptor);
		AddonModel addon = new AddonModel();
		addon.setAddonId(ADDON_ID);
		Page page = new Page("Page 1", "");
		page.getModules().add(addon);
		
		UpdatePageAddons updater = new UpdatePageAddons(descriptors);
		updater.update(page);

		assertEquals(13, addon.getPropertyCount());
		assertEquals("Options", addon.getProperty(12).getName());
		
		IListProperty optionsProperty = (IListProperty) addon.getProperty(12);
		assertEquals(1, optionsProperty.getChildrenCount());
	}


	private AddonDescriptor loadDescriptor() throws SAXException, IOException {

		InputStream inputStream = getClass().getResourceAsStream("testdata/addon-descriptor.xml");
		XMLParserMockup xmlParser = new XMLParserMockup();
		Element element = xmlParser.parser(inputStream);
		
		AddonDescriptor descriptor = new AddonDescriptor("1", "");
		descriptor.load(element, "");
		return descriptor;
	}

	
	/**
	 * Sprawdzenie aktualizacji elementów listy
	 */
	@Test
	public void updateListItem() throws IOException, SAXException {
		
		AddonDescriptor descriptor = loadDescriptor();

		HashMap<String, AddonDescriptor> descriptors = new HashMap<String, AddonDescriptor>();
		descriptors.put(ADDON_ID, descriptor);
		AddonModel addon = new AddonModel();
		addon.setAddonId(ADDON_ID);
		Page page = new Page("Page 1", "");
		page.getModules().add(addon);
		
		UpdatePageAddons updater = new UpdatePageAddons(descriptors);
		updater.update(page);

		List<AddonProperty> properties = descriptor.getProperties();
		for(AddonProperty property : properties){
			if(property.getType().compareTo("list") == 0){
				property.addSubProperty(new AddonProperty("listItem", "LIST_ITEM", "string"));
			}
		}
		
		updater.update(page);
		
		assertEquals(13, addon.getPropertyCount());
		assertEquals("Options", addon.getProperty(12).getName());
		
		IListProperty optionsProperty = (IListProperty) addon.getProperty(12);
		assertEquals(1, optionsProperty.getChildrenCount());
		
		IPropertyProvider provider = optionsProperty.getChild(0);
		assertEquals(3, provider.getPropertyCount());
	}

	
}
