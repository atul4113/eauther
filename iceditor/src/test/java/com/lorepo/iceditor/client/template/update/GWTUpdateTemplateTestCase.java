package com.lorepo.iceditor.client.template.update;

import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;

import org.custommonkey.xmlunit.DetailedDiff;
import org.custommonkey.xmlunit.Diff;
import org.custommonkey.xmlunit.ElementNameAndAttributeQualifier;
import org.custommonkey.xmlunit.XMLAssert;
import org.custommonkey.xmlunit.XMLUnit;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mockito;
import org.powermock.reflect.Whitebox;
import org.xml.sax.SAXException;

import com.googlecode.gwt.test.GwtModule;
import com.googlecode.gwt.test.GwtTest;
import com.lorepo.iceditor.client.template.UpdateTemplateTask;
import com.lorepo.iceditor.client.utils.content.ContentFactoryMockup;
import com.lorepo.icplayer.client.ContentDataLoader;
import com.lorepo.icplayer.client.model.Content;


@GwtModule("com.lorepo.iceditor.Iceditor")
public class GWTUpdateTemplateTestCase extends GwtTest {
	private UpdateTemplateTask task;
	
	@Before
	public void setUp() throws ParserConfigurationException, SAXException, IOException, TransformerException {
		XMLUnit.setIgnoreWhitespace(true);
		XMLUnit.setIgnoreComments(true);
		XMLUnit.setIgnoreDiffBetweenTextAndCDATA(true);
		XMLUnit.setNormalizeWhitespace(true);
		XMLUnit.setIgnoreAttributeOrder(true);
		
		this.task = new UpdateTemplateTask();
		ContentDataLoader contentLoaderMock = Mockito.mock(ContentDataLoader.class);
		Whitebox.setInternalState(this.task, "addonLoader", contentLoaderMock);
	}
	
	@Test
	public void updateTemplateV0HaveToOverrideDefaultLayoutStyles() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV0/contentV2.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV0/themeV0.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/themeV0/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateMissingLayoutsFromTemplateHaveToBeCopiedContentV0() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/missingLayouts/contentV0.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/missingLayouts/resultV2FromV0.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateMissingLayoutsFromTemplateHaveToBeCopiedContentV2AndAddonDescriptors() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/missingLayouts/contentV2MissingSomeAddonDescriptors.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/missingLayouts/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateMissingLayoutsFromTemplateHaveToBeCopiedContentV2() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/missingLayouts/contentV2MissingSomeLayouts.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/missingLayouts/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateMissingAndDifferentAttributesV2() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/missingAndDifferentAttributes/contentV2.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/missingAndDifferentAttributes/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();

		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateOverrideStylesWhenNamesMatch() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/differentThresholds/contentV2.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/differentThresholds/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateOverrideStylesWhenThresholdsMatch() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/differentNames/contentV2.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/differentNames/resultV2.xml");
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateOverrideDefaultLayoutsStyles() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/defaultDifferentNamesAndThresholds/contentV2Default.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/defaultDifferentNamesAndThresholds/resultV2Default.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
	
	@Test
	public void updateTemplateAddingLayoutWithOverlappingThreshold() throws SAXException, IOException {
		Content content = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/addingLayoutsThresholdsOverlapping/contentV2.xml");
		Content theme = ContentFactoryMockup.getInstanceWithAllPages().loadFromFile("testdata/update_template/addingLayoutsThresholdsOverlapping/themeV2.xml");
		String expectedXML = ContentFactoryMockup.getInstanceWithAllPages().getXMLFromFile("testdata/update_template/addingLayoutsThresholdsOverlapping/resultV2.xml");
		
		
		Content contentResult = this.task.execute(theme, content);
		String result = contentResult.toXML();
		
		
		Diff diff = new Diff(expectedXML, result);
		diff.overrideElementQualifier(new ElementNameAndAttributeQualifier());
		DetailedDiff myDiff = new DetailedDiff(diff);
		
		XMLAssert.assertXMLEqual(myDiff, true);
	}
}