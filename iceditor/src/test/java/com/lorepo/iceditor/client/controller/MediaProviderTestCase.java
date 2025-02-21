package com.lorepo.iceditor.client.controller;

import static org.junit.Assert.assertEquals;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

import org.junit.Test;
import org.xml.sax.SAXException;

import com.google.gwt.xml.client.Element;
import com.lorepo.iceditor.client.controller.MediaProviderImpl;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;
import com.lorepo.icplayer.client.mockup.xml.XMLParserMockup;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.xml.content.parsers.ContentParser_v0;

public class MediaProviderTestCase {

	@Test
	public void movePage() throws SAXException, IOException {
		Content model = this.getContentFromFile();
		
		MediaProviderImpl provider = new MediaProviderImpl(model, null);
		
		assertEquals(3, provider.getMediaCount(MediaType.IMAGE));
	}
	
	private Content getContentFromFile() throws SAXException, IOException {
		InputStream inputStream = getClass().getResourceAsStream("testdata/content.xml");
		XMLParserMockup xmlParser = new XMLParserMockup();
		Element element = xmlParser.parser(inputStream);
		
		ContentParser_v0 parser = new ContentParser_v0();
		parser.setPagesSubset(new ArrayList<Integer> ());
		
		return (Content) parser.parse(element);
	}

}
