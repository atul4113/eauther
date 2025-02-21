package com.lorepo.iceditor.client.utils.styleeditor;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.io.StringWriter;
import java.io.Writer;

import org.junit.Test;

import com.lorepo.iceditor.client.utils.styleeditor.mockup.DisplayMockup;
import com.lorepo.iceditor.client.utils.styleeditor.mockup.ModelMockup;
import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenter;

public class PresenterTestCase {

	@Test
	public void enableDisplay() throws IOException {
		
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test");
		
		presenter.setView(view);

		presenter.setModule(model);
		assertTrue(view.isEnabled());
		
		presenter.setModule(null);
		assertFalse(view.isEnabled());
	}
	
	@Test
	public void inlineStyle() throws IOException {
		
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test");
		
		presenter.setView(view);

		presenter.setModule(model);
		assertEquals("background-color:red;\ncolor:yellow;\n", view.getInlineStyles());
		
		presenter.setModule(null);
		assertEquals("", view.getInlineStyles());
	}

	
	@Test
	public void classCount() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals(3, view.getClassNames().size());
	}
	
	@Test
	public void classNameLikeModuleName() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("text");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertFalse(view.getClassNames().contains("text"));
		assertTrue(view.getClassNames().contains("text1"));
	}

	
	@Test
	public void classCountIgnoreCase() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("Test");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals(3, view.getClassNames().size());
	}

	
	@Test
	public void classNoClasses() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test2");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals(1, view.getClassNames().size());
	}

	
	@Test
	public void classNotOnList() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test2");
		model.setCssClass("Myclass");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals(2, view.getClassNames().size());
		assertEquals(" ", view.getClassNames().get(0));
		assertEquals("Myclass", view.getClassNames().get(1));
	}

	
	@Test
	public void prefixWithSpace() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("Progress Page");
		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals(4, view.getClassNames().size());
	}

	
	@Test
	public void saveClassName() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("Progress Page");
		
		presenter.setCSS(css);
		presenter.setView(view);
		presenter.setModule(model);
		
		view.getListener().onClassNameChanged("MyClassName");
		
		assertEquals("MyClassName", model.getStyleClass());
	}

	
	@Test
	public void saveInlineStyles() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("Progress Page");
		
		presenter.setCSS(css);
		presenter.setView(view);
		presenter.setModule(model);
		
		view.getListener().onInlineStyleChanged("abc");
		
		assertEquals("abc", model.getInlineStyle());
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
	
	@Test
	public void setSelection() throws IOException {
		
		String css = loadStringFromTestdata("testdata/classes2.css");
		StyleEditorPresenter presenter = new StyleEditorPresenter();
		DisplayMockup view = new DisplayMockup();
		ModelMockup model = new ModelMockup("test");
		
		model.setCssClass("testtoolbar");		
		presenter.setCSS(css);
		presenter.setView(view);

		presenter.setModule(model);
		
		assertEquals("testtoolbar", view.getSelectedName());
	}

	
}
