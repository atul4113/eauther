package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.event.dom.client.*;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.RichTextArea;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.utils.UUID;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;

/**
 * We use an inner EventListener class to avoid exposing event methods on the
 * RichTextToolbar itself.
 */
class EventListener implements ClickHandler, ChangeHandler, KeyUpHandler {

	private final RichTextToolbar richTextToolbar;


	public EventListener(RichTextToolbar richTextToolbar) {
		this.richTextToolbar = richTextToolbar;
		id = UUID.uuid(16);
	}


	@Override
	public void onChange(ChangeEvent event) {

		if(richTextToolbar.textFormatter == null){
			return;
		}

		Object sender = event.getSource();
		if (sender == this.richTextToolbar.fonts) {
			this.richTextToolbar.textFormatter.setFontName(this.richTextToolbar.fonts.getValue(this.richTextToolbar.fonts.getSelectedIndex()));
			this.richTextToolbar.fonts.setSelectedIndex(0);
		} else if (sender == this.richTextToolbar.fontSizes) {
			this.richTextToolbar.textFormatter.setFontSize(RichTextToolbar.fontSizesConstants[this.richTextToolbar.fontSizes.getSelectedIndex() - 1]);
			this.richTextToolbar.fontSizes.setSelectedIndex(0);
		}
	}


	@Override
	public void onClick(ClickEvent event) {

		if(richTextToolbar.textFormatter == null){
			return;
		}

		Object sender = event.getSource();

		if (sender == this.richTextToolbar.bold) {
			this.richTextToolbar.textFormatter.toggleBold();
		} else if (sender == this.richTextToolbar.italic) {
		    this.richTextToolbar.textFormatter.toggleItalic();
		} else if (sender == this.richTextToolbar.underline) {
		    this.richTextToolbar.textFormatter.toggleUnderline();
		} else if (sender == this.richTextToolbar.subscript) {
		    this.richTextToolbar.textFormatter.toggleSubscript();
		} else if (sender == this.richTextToolbar.superscript) {
		    this.richTextToolbar.textFormatter.toggleSuperscript();
		} else if (sender == this.richTextToolbar.strikethrough) {
			this.richTextToolbar.textFormatter.toggleStrikethrough();
		} else if (sender == this.richTextToolbar.foreColor) {
			showColorPickerForegroundColor();
		} else if (sender == this.richTextToolbar.backColor) {
			showColorPickerBackgroundColor();
		} else if (sender == this.richTextToolbar.indent) {
			this.richTextToolbar.textFormatter.rightIndent();
		} else if (sender == this.richTextToolbar.outdent) {
			this.richTextToolbar.textFormatter.leftIndent();
		} else if (sender == this.richTextToolbar.justifyLeft) {
		    this.richTextToolbar.textFormatter.setJustification(RichTextArea.Justification.LEFT);
		} else if (sender == this.richTextToolbar.justifyCenter) {
		    this.richTextToolbar.textFormatter.setJustification(RichTextArea.Justification.CENTER);
		} else if (sender == this.richTextToolbar.justifyRight) {
		    this.richTextToolbar.textFormatter.setJustification(RichTextArea.Justification.RIGHT);
		} else if (sender == this.richTextToolbar.insertImage) {
		    insertImage();
        } else if (sender == this.richTextToolbar.insertAudio) {
            insertAudio();
		} else if (sender == this.richTextToolbar.createLink) {
		    String url = Window.prompt("Enter a link URL:", "http://");
		    if (url != null) {
		    	this.richTextToolbar.textFormatter.createLink(url);
		    }
		} else if (sender == this.richTextToolbar.removeLink) {
			this.richTextToolbar.textFormatter.removeLink();
		} else if (sender == this.richTextToolbar.hr) {
			this.richTextToolbar.textFormatter.insertHorizontalRule();
		} else if (sender == this.richTextToolbar.ol) {
			this.richTextToolbar.textFormatter.insertOrderedList();
		} else if (sender == this.richTextToolbar.ul) {
			this.richTextToolbar.textFormatter.insertUnorderedList();
		} else if (sender == this.richTextToolbar.removeFormat) {
			removeAllFormatting();
		} else if (sender == this.richTextToolbar.richText) {
		    // We use the RichTextArea's onKeyUp event to update the toolbar status.
			// This will catch any cases where the user moves the cursur using the
			// keyboard, or uses one of the browser's built-in keyboard shortcuts.
		    this.richTextToolbar.updateStatus();
		}
	}

	// ---------------------------------------------------------------- ColorPicker

	public void showColorPickerForegroundColor() {
		showColorPicker( getColorPickerConfigForegroundChange(this, getId(), this.richTextToolbar.panelId ) );
	}

	public void showColorPickerBackgroundColor() {
		showColorPicker( getColorPickerConfigBackgroundChange(this, getId(), this.richTextToolbar.panelId ) );
	}

	public native void showColorPicker(Object configuration) /*-{
		$wnd.window.ColorPicker.showColorPicker(configuration);
	}-*/;


	public native Object getColorPickerConfigForegroundChange(EventListener javaThis, String id, String posAt) /*-{
		return {
			positionAt: posAt,
			elementId: "#foreground-text-colorpicker" + id,
			okCallback : function(color) { javaThis.@com.lorepo.iceditor.client.ui.widgets.properties.editors.EventListener::setForegroundColor(Ljava/lang/String;)(color); }
		}
	}-*/;

	public native Object getColorPickerConfigBackgroundChange(EventListener javaThis, String id, String posAt) /*-{
		return {
			positionAt: posAt,
			elementId: "#background-text-colorpicker" + id,
			okCallback : function(color) { javaThis.@com.lorepo.iceditor.client.ui.widgets.properties.editors.EventListener::setBackgroundColor(Ljava/lang/String;)(color); }
		}
	}-*/;


	public void setForegroundColor( String color ) {
		if (color == "000000" || color == "0" || color == "000") {
			color = "000001";
		}
		if (color == "") { // that should come only when user clicks None button
			color = "000000"; // Full black is a special value, that will make GWT textFormatter erase color (also removes spans)
		}

		richTextToolbar.textFormatter.setForeColor("#" + color);
	}

	public void setBackgroundColor( String color ) {
		if (color != "")
			color = "#" + color;
		// todo: richTextToolbar.textFormatter.removeFormat(); could be used to emulate setting Default bg color
		richTextToolbar.textFormatter.setBackColor(color);
	}

	private String id;
	public String getId() { return id; }


	// ----------------------------------------------------------------

	private void insertImage() {
		if (this.richTextToolbar.fileSelector != null) {
			final FileSelectorWidget fileSelector = this.richTextToolbar.fileSelector;

			fileSelector.setMediaType(MediaType.IMAGE);
			fileSelector.setShouldCloseWidgetLocker(true);
			fileSelector.setListener(new FileSelectorEventListener() {
				@Override
				public void onSelected(String filePath) {
					fileSelector.hide();

					EventListener.this.richTextToolbar.textFormatter.insertImage(filePath);

					RenderEditor editor = getCurrentEditor();
					if (editor != null) {
						editor.imageAdded();
					}
				}
			});

			fileSelector.show();
		}
	}

	private void insertAudio() {
		if (this.richTextToolbar.fileSelector != null) {
			final FileSelectorWidget fileSelector = this.richTextToolbar.fileSelector;
			fileSelector.setMediaType(MediaType.AUDIO);
			fileSelector.setShouldCloseWidgetLocker(true);
			fileSelector.setListener(new FileSelectorEventListener() {
				@Override
				public void onSelected(String filePath) {
					fileSelector.hide();
					EventListener.this.richTextToolbar.textFormatter.insertHTML("\\audio{" + filePath + "}");
					RenderEditor editor = getCurrentEditor();
					if (editor != null) {
						reloadEditorArea(editor);
						editor.audioAdded();
					}

				}
			});
			fileSelector.show();
		}
	}

	private void reloadEditorArea(RenderEditor editor){
		editor.changeRenderOption();
		editor.changeRenderOption();
	}

	private void removeAllFormatting() {
		RenderEditor editor = this.getCurrentEditor();

		if (editor == null){
			return;
		}

		boolean renderGapIsChecked = editor.getRenderOption();

		if (renderGapIsChecked){
			editor.changeRenderOption();
		}

		RichTextArea textField  = richTextToolbar.getEditor();

		String text = textField.getText();
		text = text.replaceAll("\\<!--.*\\-->", "");
		textField.setText(text);

		if (renderGapIsChecked){
			editor.changeRenderOption();
		}
	}

	private RenderEditor getCurrentEditor() {
		HTMLEditorWidget htmlEditor = MainPageUtils.getAppFrame().getHTMLEditor();

		if (htmlEditor.isVisible()){
			return htmlEditor;
		}

		ItemsEditorWidget itemsEditor = MainPageUtils.getAppFrame().getItemsEditor();

		if (itemsEditor.isVisible()) {
			return itemsEditor;
		}

		StaticItemsEditorWidget staticEditor = MainPageUtils.getAppFrame().getStaticItemsEditor();

		if (staticEditor.isVisible()){
			return staticEditor;
		}

		return null;
	}


	@Override
	public void onKeyUp(KeyUpEvent event) {

		if (event.getSource() == this.richTextToolbar.richText) {
	        // We use the RichTextArea's onKeyUp event to update the toolbar status.
	        // This will catch any cases where the user moves the cursor using the
	        // keyboard, or uses one of the browser's built-in keyboard shortcuts.
	        this.richTextToolbar.updateStatus();
		}
    }

  }