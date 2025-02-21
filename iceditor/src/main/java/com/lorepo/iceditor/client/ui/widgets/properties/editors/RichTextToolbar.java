/*
 * Copyright 2007 Google Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
//package com.google.gwt.sample.kitchensink.client;
package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PushButton;
import com.google.gwt.user.client.ui.RichTextArea;
import com.google.gwt.user.client.ui.ToggleButton;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.richTextToolbar.*;
import com.lorepo.icf.widgets.richeditor.i18n.RichTextConstants;
import com.lorepo.icf.widgets.richeditor.resources.RichTextToolbarResources;

/**
 * 
 * A sample toolbar for use with {@link RichTextArea}. It provides a simple UI
 * for all rich text formatting, dynamically displayed only for the available
 * functionality.
 */
public class RichTextToolbar extends Composite {
	
  
	static final RichTextArea.FontSize[] fontSizesConstants = new RichTextArea.FontSize[] {
		RichTextArea.FontSize.XX_SMALL, RichTextArea.FontSize.X_SMALL,
		RichTextArea.FontSize.SMALL, RichTextArea.FontSize.MEDIUM,
		RichTextArea.FontSize.LARGE, RichTextArea.FontSize.X_LARGE,
		RichTextArea.FontSize.XX_LARGE
	};
	
	public String panelId;

	private RichTextToolbarResources images = RichTextToolbarResources.INSTANCE;
	private RichTextConstants strings = (RichTextConstants) GWT.create(RichTextConstants.class);
	private EventListener listener = new EventListener(this);

	protected RichTextArea richText;
	protected RichTextArea.Formatter textFormatter;
	protected FileSelectorWidget fileSelector;

	private VerticalPanel outer = new VerticalPanel();
	private HorizontalPanel topPanel = new HorizontalPanel();
	private FlowPanel bottomPanel = new FlowPanel();
	ToggleButton bold;
	ToggleButton italic;
	ToggleButton underline;
	ToggleButton subscript;
	ToggleButton superscript;
	ToggleButton strikethrough;
	PushButton foreColor;
	PushButton backColor;
	PushButton indent;
	PushButton outdent;
	PushButton justifyLeft;
	PushButton justifyCenter;
	PushButton justifyRight;
	PushButton hr;
	PushButton ol;
	PushButton ul;
	PushButton insertImage;
	PushButton insertAudio;
	PushButton createLink;
	PushButton removeLink;
	PushButton removeFormat;

	ListBox fonts;
	ListBox fontSizes;

	private HandlerRegistration keyUpHandler;
	private HandlerRegistration clickHandler;
	
	private Map<String, Widget> configurableWidgets;
  
	/**
	 * Creates a new toolbar that drives the given rich text area.
	 * 
	 * @param richText the rich text area to be controlled
	 */
	public RichTextToolbar(String panelId) {
    
		createUI();
	
	    createTopPanel();
	    createBottomPanel();
	    setDefaultVisibility();
	    createConfigurableWidgets();
	    this.panelId = panelId;
	}
	
	public void setModule(String moduleType) {
		VisibilityConfiguration conf = ConfigurationManager.getConfiguration(moduleType);
		
		changeVisibility(conf.getConfiguration());
	}

	private void createUI() {
		outer.add(topPanel);
		outer.add(bottomPanel);
		topPanel.setWidth("100%");
		bottomPanel.setWidth("100%");
	
	    initWidget(outer);
	    setStyleName("gwt-RichTextToolbar");
	}


	private void createTopPanel() {
		topPanel.add(bold = createToggleButton(images.bold(), strings.bold()));
		topPanel.add(italic = createToggleButton(images.italic(), strings.italic()));
		topPanel.add(underline = createToggleButton(images.underline(), strings.underline()));
		topPanel.add(subscript = createToggleButton(images.subscript(),strings.subscript()));
		topPanel.add(superscript = createToggleButton(images.superscript(), strings.superscript()));
		topPanel.add(strikethrough = createToggleButton(images.strikeThrough(), strings.strikeThrough()));
		topPanel.add(foreColor = createPushButton(images.foreColors(), strings.foreColors()));
		topPanel.add(backColor = createPushButton(images.backColors(), strings.backColors()));
		topPanel.add(justifyLeft = createPushButton(images.justifyLeft(), strings.justifyLeft()));
		topPanel.add(justifyCenter = createPushButton(images.justifyCenter(), strings.justifyCenter()));
		topPanel.add(justifyRight = createPushButton(images.justifyRight(), strings.justifyRight()));
		topPanel.add(indent = createPushButton(images.indent(), strings.indent()));
		topPanel.add(outdent = createPushButton(images.outdent(), strings.outdent()));
		topPanel.add(hr = createPushButton(images.hr(), strings.hr()));
		topPanel.add(ol = createPushButton(images.ol(), strings.ol()));
		topPanel.add(ul = createPushButton(images.ul(), strings.ul()));
		topPanel.add(insertImage = createPushButton(images.insertImage(), strings.insertImage()));
		topPanel.add(insertAudio = createPushButton(images.insertAudio(), strings.insertAudio()));
		topPanel.add(createLink = createPushButton(images.createLink(), strings.createLink()));
		topPanel.add(removeLink = createPushButton(images.removeLink(), strings.removeLink()));
		topPanel.add(removeFormat = createPushButton(images.removeFormat(), strings.removeFormat()));

		foreColor.getElement().setId("foreground-text-colorpicker" + listener.getId());
		backColor.getElement().setId("background-text-colorpicker" + listener.getId());

	}


	private void createBottomPanel() {
	    bottomPanel.add(fonts = createFontList());
	    bottomPanel.add(fontSizes = createFontSizes());
	}


	public void setRichTextWidget(RichTextArea richText) {

		if(keyUpHandler != null){
			keyUpHandler.removeHandler();
		}
		if(clickHandler != null){
			clickHandler.removeHandler();
		}

		if(richText != null){
			this.richText = richText;
			this.textFormatter = richText.getFormatter();
			keyUpHandler = richText.addKeyUpHandler(listener);
			clickHandler = richText.addClickHandler(listener);
		}
		else{
			this.richText = null;
			this.textFormatter = null;
		}
	}

	// Fix an issue with blockQuote on FF
	public void fixIndentIssue() {
		if (richText == null) return;
		
		final String blockQuoteStyle = "margin: 0 0 0 40px; border: none; padding: 0px;";
		String html = richText.getHTML();

		richText.setHTML(html.replaceAll("<blockquote>", "<blockquote style=\"" + blockQuoteStyle + "\">"));
	}
	
	public void setFileSelector(FileSelectorWidget fileSelector) {
		this.fileSelector = fileSelector;
	}
	
	private void changeVisibility(Map<String, Boolean> options) {
		for (Entry<String, Boolean> entry : options.entrySet()) {
			Widget widget = configurableWidgets.get(entry.getKey());
			
			if (widget != null) {
				widget.setVisible(entry.getValue());
			}
		}
	}
  
	private ListBox createFontList() {
    
		ListBox lb = new ListBox();
	    lb.addChangeHandler(listener);
	    lb.setVisibleItemCount(1);
	
	    lb.addItem(strings.font(), "");
	    lb.addItem(strings.normal(), "");
	    lb.addItem("Times New Roman", "Times New Roman");
	    lb.addItem("Arial", "Arial");
	    lb.addItem("Courier New", "Courier New");
	    lb.addItem("Georgia", "Georgia");
	    lb.addItem("Trebuchet", "Trebuchet");
	    lb.addItem("Verdana", "Verdana");
	    return lb;
	}

	private ListBox createFontSizes() {
    
		ListBox lb = new ListBox();
	    lb.addChangeHandler(listener);
	    lb.setVisibleItemCount(1);
	
	    lb.addItem(strings.size());
	    lb.addItem(strings.xxsmall());
	    lb.addItem(strings.xsmall());
	    lb.addItem(strings.small());
	    lb.addItem(strings.medium());
	    lb.addItem(strings.large());
	    lb.addItem(strings.xlarge());
	    lb.addItem(strings.xxlarge());
	    return lb;
	}

  
	private PushButton createPushButton(ImageResource img, String tip) {
	    PushButton pb = new PushButton(new Image(img));
	    pb.addClickHandler(listener);
	    pb.setTitle(tip);
	    return pb;
	}

  
	private ToggleButton createToggleButton(ImageResource img, String tip) {
	    ToggleButton tb = new ToggleButton(new Image(img));
	    tb.addClickHandler(listener);
	    tb.setTitle(tip);
	    return tb;
	}
	
	private void setDefaultVisibility() {
		this.insertAudio.setVisible(false);
	}

	private void createConfigurableWidgets() {
		configurableWidgets = new HashMap<String, Widget>();
		configurableWidgets.put(DefaultOptionVisiblityConfiguration.insertAudioKey, insertAudio);
	}

	/**
   	* Updates the status of all the stateful buttons.
   	*/
	protected void updateStatus() {
    
		bold.setDown(textFormatter.isBold());
		italic.setDown(textFormatter.isItalic());
		underline.setDown(textFormatter.isUnderlined());
		subscript.setDown(textFormatter.isSubscript());
		superscript.setDown(textFormatter.isSuperscript());
		strikethrough.setDown(textFormatter.isStrikethrough());
	}


	public RichTextArea getEditor() {
		return richText;
	}
}

