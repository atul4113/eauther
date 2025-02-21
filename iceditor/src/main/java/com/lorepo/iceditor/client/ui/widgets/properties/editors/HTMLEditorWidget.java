package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.http.client.*;
import com.google.gwt.query.client.Function;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.*;
import com.lorepo.iceditor.client.browser.NavigatorUtil;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.modals.*;
import com.lorepo.iceditor.client.ui.widgets.utils.GapsParserUtil;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.iceditor.client.utils.properties.CustomRichTextArea;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider;
import com.lorepo.icplayer.client.utils.DomElementManipulator;

import java.util.ArrayList;
import java.util.List;

import static com.google.gwt.query.client.GQuery.$;

public class HTMLEditorWidget extends Composite implements RenderEditor {

	private static TextEditorWidgetUiBinder uiBinder = GWT
			.create(TextEditorWidgetUiBinder.class);

	interface TextEditorWidgetUiBinder extends
			UiBinder<Widget, HTMLEditorWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel contents;
	
	@UiField AnchorElement apply;
	@UiField AnchorElement save;
	
	@UiField AnchorElement closeBtn;
	
	private RichTextArea textArea;
	private RichTextToolbar toolbar;
	
	private String startText;
	private ModalsWidget modals;
	private AddGapWidget addGap = new AddGapWidget();
	private boolean isInitialized = false;
	private String shouldRenderURL = "/save_should_render";
	private boolean isRenderMode = true;
	private JavaScriptObject range;

	public HTMLEditorWidget() {
		initWidget(uiBinder.createAndBindUi(this));

		String panelId = "textEditorPage";
		panel.getElement().setId(panelId);
		contents.getElement().setId("textEditorPage-contents");
		hide();
		
		SimplePanel textAreaWrapper = new SimplePanel();
		textAreaWrapper.getElement().setClassName("iframe-wrapper");
		
		textArea = new CustomRichTextArea();
		textArea.getElement().addClassName("richTextEditArea");

		toolbar = new RichTextToolbar(panelId);
		toolbar.setRichTextWidget(textArea);
		// todo Ids are duplicated among all instances of HTMLEditorWidget, ItemsEditorWidget etc.
		// Used most likely only by css to style. Would be better to change it to class selector.
		toolbar.getElement().setId("richTextEditor");  
		
		contents.add(toolbar);
		contents.add(addGap);
		
		textAreaWrapper.add(textArea);
		contents.add(textAreaWrapper);
		
		apply.setId("editorApply");
		save.setId("editorSave");
		
		updateElementsText();
		initJSAPI(this);
	}

	private native void initJSAPI(HTMLEditorWidget x) /*-{
	    $wnd.isHTMLEditorModified = function() {
	        return x.@com.lorepo.iceditor.client.ui.widgets.properties.editors.HTMLEditorWidget::isModified()();
	    }
	}-*/;

	public void show() {
		MainPageUtils.show(panel);
		startText = getText();

		if (addGap.renderedOption.isChecked()) {
			isRenderMode = true;
			restore();
		} else {
			isRenderMode = false;
			addImageAltTextHandler();
			addAudioHandler();
		}

		if (!isInitialized) {
			updateView();
			isInitialized = true;
		}
	}

	private void removeHandlers() {
		$("#content").off("mousedown touchstart dblclick");
		$(".mainPageCloseBtn").off("click");
	}

	public void hide() {
		removeHandlers();

		WidgetLockerController.hide();
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}

	public native String unwrapItems() /*-{
		function replaceWithItemDef(items, attribute) {
			$_.each(items, function(i, el) {
				$_(el).replaceWith($_(el).attr(attribute));
			});
		}

		var syntax = "",
			$_ = $wnd.$,
			clone = $_(".iframe-wrapper").find("iframe").contents().clone(),
			gapItems = clone.find("input[data-gap]");
			audioItems = clone.find("input[data-audio-value]");
			linkItems = clone.find("a[data-gap]");

		replaceWithItemDef(gapItems, "data-gap-value");
		replaceWithItemDef(linkItems, "data-gap-value");
		replaceWithItemDef(audioItems, "data-audio-value");

		return clone.find('body').html();
	}-*/;

	public void setText(String text) {
		String HTMLFinal = addGap.renderedOption.isChecked() ? GapsParserUtil.render(text) : text;
		textArea.setHTML(HTMLFinal);
	}

	public String getText() {
		toolbar.fixIndentIssue();
		String returnedText = unwrapItems();
		return returnedText;
	}

	public void setFileSelector(FileSelectorWidget fileSelector) {
		toolbar.setFileSelector(fileSelector);
	}

	public boolean isModified() {
		return !getText().equals(startText);
	}

	private void saveChanges(final MainPageEventListener listener) {
		getModals().addModal(DictionaryWrapper.get("save_changes"), new QuestionModalListener() {
			@Override
			public void onDecline() {
				reset();
				hide();
			}

			@Override
			public void onAccept() {
				removeHandlers();
				listener.onSave();
				reset();
				saveViewRendered();
			}
		});
	}

	public void setListener(final MainPageEventListener listener) {
		if (listener == null) {
			return;
		}

		Event.sinkEvents(apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}

				saveViewRendered();
				reset();
				listener.onApply();
				restore();
			}
		});

		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt() && Event.ONTOUCHEND != event.getTypeInt()) {
					return;
				}

				removeHandlers();

				saveViewRendered();
				reset();
				restore();
				listener.onSave();
			}
		});

		$(".mainPageCloseBtn").on("click", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("htmlEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("htmlEditorPage")) {
					hide();
				}
			}
		});

		$("#content").on("mousedown", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("htmlEditorPage")) {
					saveChanges(listener);
				} else if (MainPageUtils.isWindowOpened("htmlEditorPage")) {
					hide();
				}
			}
		});

		Event.sinkEvents(addGap.addGapOption, Event.ONCHANGE);
		Event.setEventListener(addGap.addGapOption, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				insertGap(addGap.addGapOption.getValue());
				addGap.addGapOption.setSelectedIndex(0);
			}
		});

		Event.sinkEvents(addGap.renderedOption, Event.ONCHANGE);
		Event.setEventListener(addGap.renderedOption, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (addGap.renderedOption.isChecked()) {
					isRenderMode = true;
					textArea.setHTML(GapsParserUtil.render(textArea.getHTML()));
					restore();
				} else {
					isRenderMode = false;
					textArea.setHTML(unwrapItems());
				}
			}
		});

		Event.sinkEvents(addGap.addAltText, Event.ONCLICK);
		Event.setEventListener(addGap.addAltText, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				addAltTextWidget(null,null);
			}
		});
	}
	
	public void setModuleName(String name) {
		toolbar.setModule(name);
	}

	private void insertGap(String selectedOption) {
		range = getRange();

		if (selectedOption.equals("editable")) {
			addSingleGapWidget(null, null);
		} else if (selectedOption.equals("filled")) {
			addSingleFilledGapWidget(null, null);
		} else if (selectedOption.equals("dropdown")) {
			addDropDownGapWidget(null, null);
		}
	}
	
	private void addHandler() {
		final GQuery iframeContent = $(".iframe-wrapper").find("iframe").contents();
		
		final GQuery editableGaps = iframeContent.find("input[data-gap='editable']");
		final GQuery filledGaps = iframeContent.find("input[data-gap='filled']");
		final GQuery dropdownGaps = iframeContent.find("input[data-gap='dropdown']");

		editableGaps.on("mousedown", new Function() {
			public boolean f(Event e) {	
				String gapDefinition = this.getElement().getAttribute("data-gap-value");
				List<String> values = GapsParserUtil.getEditableGaps(gapDefinition);

				addSingleGapWidget(this.getElement(), values);
				
				editableGaps.off("mousedown");
				
				return false;
			}
		});
		
		filledGaps.on("mousedown", new Function() {
			public boolean f(Event e) {
				String gapDefinition = this.getElement().getAttribute("data-gap-value");
				List<String> values = GapsParserUtil.getFilledGaps(gapDefinition);
				
				addSingleFilledGapWidget(this.getElement(), values);
				
				filledGaps.off("mousedown");
				
				return false;
			}
		});
		
		dropdownGaps.on("mousedown", new Function() {
			public boolean f(Event e) {
				String gapDefinition = this.getElement().getAttribute("data-gap-value");
				List<String> values = GapsParserUtil.getDropdownGaps(gapDefinition);

				addDropDownGapWidget(this.getElement(), values);
				dropdownGaps.off("mousedown");
				
				return false;
			}
		});
	}
	
	private void insertHTML(String html, JavaScriptObject selectionRange) {
		if (NavigatorUtil.isIEBrowser()) {
			insert(html, selectionRange);
		} else {
			toolbar.textFormatter.insertHTML(html);
		}
	}
	
	private native void insert(String html, JavaScriptObject selectionRange) /*-{
		var selection, range;

		if (selectionRange) {
	    	selection = $wnd.$(".iframe-wrapper").find("iframe")[0].contentWindow.getSelection();
	        if (selection) {
	            selection.removeAllRanges();
	            selection.addRange(selectionRange);
	        }
	    }
	
	    if (selection) {
	        if (selection.getRangeAt && selection.rangeCount) {
	            range = selection.getRangeAt(0);
	            range.deleteContents();
	
	            // Range.createContextualFragment() would be useful here but is
	            // non-standard and not supported in all browsers (IE9, for one)
	            var doc = $wnd.$(".iframe-wrapper").find("iframe")[0].contentWindow.document,
	            	el = doc.createElement("div"),
	            	frag = doc.createDocumentFragment(), node, lastNode;
	
	            el.innerHTML = html;

	            while ( (node = el.firstChild) ) {
	                lastNode = frag.appendChild(node);
	            }
	            range.insertNode(frag);
	            
	            // Preserve the selection
	
	            if (lastNode) {
	                range = range.cloneRange();
	                range.setStartAfter(lastNode);
	                range.collapse(true);
	                selection.removeAllRanges();
	                selection.addRange(range);
	            }
	        }
	    }
	}-*/;

	private native JavaScriptObject getRange() /*-{
		var sel = $wnd.$(".iframe-wrapper").find("iframe")[0].contentWindow.getSelection();
		  
		if (sel && sel.getRangeAt && sel.rangeCount) {
		  return sel.getRangeAt(0);
		}
		  
		return null;
	}-*/;
	
	private native String getSelection() /*-{
	    return $wnd.$(".iframe-wrapper").find("iframe")[0].contentWindow.getSelection().toString();
	}-*/;
	
	private void addSingleGapWidget(final Element element, final List<String> values) {
		String mode = element == null ? "add" : "edit";
		
		MainPageUtils.getModals().addSingleGapWidget(mode, values, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}
			
			@Override
			public void onAccept() {
				SingleGapWidget widget = MainPageUtils.getModals().getSingleGapWidget();
				DomElementManipulator inputElement = new DomElementManipulator("input");
				inputElement.setHTMLAttribute("size", (widget.getDefinition().length() - 6));
				inputElement.setHTMLAttribute("data-gap", "editable");
				inputElement.setHTMLAttribute("data-gap-value", widget.getDefinition());
				inputElement.setHTMLAttribute("readonly", true);
				
				String definition = inputElement.getHTMLCode();
				
				if (isRenderMode) {
					if (element == null) {
						insertHTML(definition, range);
					} else {
						element.setAttribute("data-gap-value", widget.getDefinition());
						element.setAttribute("size", Integer.toString(widget.getDefinition().length() - 6));
					}
				} else {
					definition = widget.getDefinition();
					insertHTML(definition, range);
				}
				
				restore();
			}
		});
	}
	
	private void addSingleFilledGapWidget(final Element element, final List<String> values) {
		String mode = element == null ? "add" : "edit";
		
		MainPageUtils.getModals().addSingleFilledGapWidget(mode, values, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}
			
			@Override
			public void onAccept() {
				SingleFilledGapWidget widget = MainPageUtils.getModals().getSingleFilledGapWidget();
				DomElementManipulator inputElement = new DomElementManipulator("input");
				inputElement.setHTMLAttribute("size", Math.max(widget.getAnswerSize(), widget.getPlaceholder().length()));
				inputElement.setHTMLAttribute("data-gap", "filled");
				inputElement.setHTMLAttribute("placeholder", widget.getPlaceholder());
				inputElement.setHTMLAttribute("data-gap-value", widget.getDefinition());
				inputElement.setHTMLAttribute("readonly", true);
				String definition = inputElement.getHTMLCode();
				
				if (isRenderMode) {
					if (element == null) {
						insertHTML(definition, range);
					} else {
						element.setAttribute("placeholder", widget.getPlaceholder());
						element.setAttribute("data-gap-value", widget.getDefinition());
						element.setAttribute("size", Integer.toString(Math.max(widget.getAnswerSize(), widget.getPlaceholder().length())));
					}
				} else {
					definition = widget.getDefinition();
					insertHTML(definition, range);
				}
				
				restore();
			}
		});
	}
	
	private void addDropDownGapWidget(final Element element, final List<String> values) {
		String mode = element == null ? "add" : "edit";
		
		MainPageUtils.getModals().addDropDownGapWidget("HTMLEditor", mode, values, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}
			
			@Override
			public void onAccept() {
				DropDownGapWidget widget = MainPageUtils.getModals().getDropDownGapWidget();
				DomElementManipulator inputElement = new DomElementManipulator("input");
				inputElement.setHTMLAttribute("value", DomElementManipulator.getFromHTMLCodeUnicode("&#9660"));
				inputElement.setHTMLAttribute("style", "text-align: right; width: 80px");
				inputElement.setHTMLAttribute("data-gap", "dropdown");
				inputElement.setHTMLAttribute("data-gap-value", widget.getDefinition());
				String definition = inputElement.getHTMLCode();
				
				if (isRenderMode) {
					if (element == null) {
						insertHTML(definition, range);
					} else {
						element.setAttribute("data-gap-value", widget.getDefinition());
					}
				} else {
					definition = widget.getDefinition();
					insertHTML(definition, range);
				}
				
				restore();
			}
		});
	}
	
	private void reset() {
		startText = getText();
	}

	public void updateElementsText() {
		apply.setInnerText(DictionaryWrapper.get("apply"));
		save.setInnerText(DictionaryWrapper.get("save"));

		$(panel.getElement()).find(".mainPageHeader h3").text(DictionaryWrapper.get("html_editor"));
	}

	public void setModals(ModalsWidget modals) {
		this.modals = modals;
	}

	private ModalsWidget getModals() {
		return modals;
	}
	
	private native void addStyles() /*-{
	    $wnd.$(".iframe-wrapper").find("iframe").contents().find("input[data-gap]").css({"cursor": "pointer"});
	}-*/;
	
	private void restore() {
		addHandler();
		addImageAltTextHandler();
		addAudioHandler();
		addStyles();
	}
	
	private native void addSelectStyle() /*-{
	    $wnd.$(".iframe-wrapper").find("iframe").contents().find("body").css({"-ms-user-select": "text"});
	}-*/;
	
	private void updateView() {
		final GQuery content = $(".iframe-wrapper").find("iframe").contents().find("body");

		addSelectStyle();
		
		content.on("keyup", new Function() {
			int length = content.find("input[data-gap]").length();
			
			public void f() {
				int currentLength = content.find("input[data-gap]").length();
				
				if (currentLength != length) {
					length = currentLength;
					restore();
				}
			}
		});
	}

	public boolean isViewRendered() {
		return addGap.renderedOption.isChecked();
	}

	public void setRenderedView(boolean shouldRender) {
		addGap.renderedOption.setChecked(shouldRender);
	}

	private void saveViewRendered() {
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, URL.encode(shouldRenderURL));
		
		String postData = "is_rendered=" + (isViewRendered() ? "1" : "0");
		builder.setHeader("Content-type", "application/x-www-form-urlencoded");

		try {
			builder.sendRequest(postData, new RequestCallback() {
				@Override
				public void onResponseReceived(Request request, Response response) {
					
				}
				
				@Override
				public void onError(Request request, Throwable exception) {
					
				}
			});
		} catch(RequestException e) {}
	}

	public void setURLToSave(String url) {
		this.shouldRenderURL = url;
	}

	public boolean getRenderOption(){
		 return addGap.isChecked();
	}

	public void changeRenderOption(){
		this.addGap.changeRenderOption();
	}

	private void addImageAltTextHandler() {
		final GQuery iframeContent = $(".iframe-wrapper").find("iframe").contents();
		
		final GQuery images = iframeContent.find("img");
		
		images.on("dblclick", new Function() {
			public boolean f(Event e) {
				String altText = this.getElement().getAttribute("alt");

				addImageAltTextWidget(this.getElement(), altText);
				images.off("dblclick");
				
				return false;
			}
		});
	}

	private void addAudioHandler() {
		final GQuery iframeContent = $(".iframe-wrapper").find("iframe").contents();
		final GQuery audio = iframeContent.find(".ic_text_audio_button ");

		audio.on("click", new Function() {
			public boolean f(Event e) {
				audio.off("click");

				final FileSelectorWidget fileSelector = toolbar.fileSelector;
				final Element audioElement = this.getElement();

				fileSelector.show();
				fileSelector.setMediaType(IMediaProvider.MediaType.AUDIO);
				fileSelector.setShouldCloseWidgetLocker(true);
				fileSelector.setListener(new FileSelectorEventListener() {
					@Override
					public void onSelected(String filePath) {
						fileSelector.hide();
						audioElement.setAttribute("data-audio-value", "\\audio{" + filePath + "}");
						audioAdded();
					}
				});

				return false;
			}
		});
	}

	private void addImageAltTextWidget(final Element element, final String value) {
		MainPageUtils.getModals().addImageAltTextWidget(value, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}

			@Override
			public void onAccept() {
				ImageAltTextWidget widget = MainPageUtils.getModals().getImageAltTextWidget();
				String altTextValue = widget.getValue();

				if (element != null) {
					if (altTextValue.isEmpty()) {
						element.removeAttribute("alt");
					} else {
						element.setAttribute("alt", altTextValue);
					}
				}

				restore();
			}
		});
	}

	private void addAltTextWidget(final Element element, final List<String> values){
		String mode = element == null ? "add" : "edit";
		String selection = getSelection();
		
		List<String> finalValues;
		if(values==null && selection.length()>0){
			finalValues = new ArrayList<String>();
			finalValues.add(selection);
		} else {
			finalValues = values;
		}
		
		MainPageUtils.getModals().addAltTextWidget(mode, finalValues, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}
			
			@Override
			public void onAccept() {
				AltTextWidget widget = MainPageUtils.getModals().getAltTextWidget();
				insertHTML(widget.getDefinition(), range);
				restore();
			}
		});
	}

	@Override
	public void imageAdded() {
		addImageAltTextHandler();
	}

	@Override
	public void audioAdded() {
		addAudioHandler();
	}
}
