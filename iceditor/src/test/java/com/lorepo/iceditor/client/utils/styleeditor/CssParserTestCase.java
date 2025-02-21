package com.lorepo.iceditor.client.utils.styleeditor;

import static org.junit.Assert.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.StringWriter;
import java.io.Writer;
import java.util.List;

import org.junit.Test;

import com.lorepo.iceditor.client.utils.ui.styleeditor.CssParser;

public class CssParserTestCase {

	@Test
	public void classNames() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes.css");
		CssParser parser = new CssParser();
		List<String> classNames = parser.findClasses(css);

		assertEquals(6, classNames.size());
		assertTrue(classNames.contains("ice_page"));
		assertTrue(classNames.contains("ice_header"));
		assertTrue(classNames.contains("ice_title"));
		assertTrue(classNames.contains("ice_imageButton"));
		assertTrue(classNames.contains("ice_naviTabs"));
		assertTrue(classNames.contains("ice_toolbar"));
	}
	
	@Test
	public void testComplexSelectors() throws IOException {
		
		String css = loadStringFromTestdata("testdata/complexSelectorsCSS.css");
		CssParser parser = new CssParser();
		List<String> classNames = parser.findClasses(css);
		
		assertEquals(6, classNames.size());
		assertTrue(classNames.contains("text-identification-element-correct"));
		assertTrue(classNames.contains("text-course-header"));
		assertTrue(classNames.contains("navigationbar-element-next"));
		assertFalse(classNames.contains("addon_text_identification"));
		assertFalse(classNames.contains("addon_Image_Identification"));
		assertFalse(classNames.contains("image_identification-element"));
		assertTrue(classNames.contains("class1"));
		assertTrue(classNames.contains("class2"));
		assertTrue(classNames.contains("class3"));
	}
	
	@Test
	public void testWhenNoStyles() throws IOException {
		
		CssParser parser = new CssParser();
		List<String> classNames = parser.findClasses(null);
		
		assertEquals(classNames, classNames);
	}
	
	private String loadStringFromTestdata(String path) throws IOException {
		
		InputStream inputStream = getClass().getResourceAsStream(path);

		Writer writer = new StringWriter();
		char[] buffer = new char[1024];
	
		try {
			Reader reader = new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
	
			int n;
			while ((n = reader.read(buffer)) != -1) {
				writer.write(buffer, 0, n);
			}
		} finally {
			inputStream.close();
		}
	
		return writer.toString();
	}
}
