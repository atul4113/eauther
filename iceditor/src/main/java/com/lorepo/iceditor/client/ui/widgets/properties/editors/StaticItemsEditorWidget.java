package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.HeadingElement;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.http.client.*;
import com.google.gwt.query.client.Function;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.ModalOpenedAction;
import com.lorepo.iceditor.client.browser.NavigatorUtil;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.modals.*;
import com.lorepo.iceditor.client.ui.widgets.properties.ModuleChangedListener;
import com.lorepo.iceditor.client.ui.widgets.utils.GapsParserUtil;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.IStaticListProperty;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider;

import java.util.ArrayList;
import java.util.List;

import static com.google.gwt.query.client.GQuery.$;

public class StaticItemsEditorWidget extends Composite implements RenderEditor {

	private static StaticItemsEditorWidgetUiBinder uiBinder = GWT
			.create(StaticItemsEditorWidgetUiBinder.class);

	interface StaticItemsEditorWidgetUiBinder extends
			UiBinder<Widget, StaticItemsEditorWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HTMLPanel list;
	@UiField HTMLPanel contents;
	
	@UiField DivElement wrapper;
	@UiField AnchorElement save;
	@UiField AnchorElement apply;
	@UiField HeadingElement title;
	@UiField AnchorElement closeButton;
	
	private AbstractAction onSave;
	private AbstractAction onEditModule;
	private ModalOpenedAction onModalOpened;
	
	private IStaticListProperty property;
	private List<StaticListItemWidget> items = new ArrayList<StaticListItemWidget>();
	
	private RichTextToolbar toolbar;
	private FileSelectorWidget fileSelector;
	private ModuleChangedListener moduleChangedListener;

	private boolean modified = false;
	private ModalsWidget modals;
	
	private AddGapWidget addGap = new AddGapWidget();
	private boolean isInitialized = false;
	private String shouldRenderURL = "/save_should_render";
	private boolean isRenderMode = true;
	private JavaScriptObject range;


	public StaticItemsEditorWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		String panelId = "staticListPage";
		panel.getElement().setId(panelId);
		hide();
		
		connectHandlers();
		
		contents.getElement().setId("propertiesPage-contents");
		toolbar = new RichTextToolbar(panelId);
		toolbar.getElement().setId("richTextEditor");
		contents.add(toolbar);
		contents.add(addGap);
		
		apply.setId("editorApply");
		save.setId("editorSave");
		
		updateElementsTexts();
	}

	private void removeHandlers() {
		$("#content").off("mousedown touchstart dblclick");
		$(".mainPageCloseBtn").off("click");
	}
	
	private void connectHandlers() {
		Event.sinkEvents(save, Event.ONCLICK);
		Event.setEventListener(save, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt() && Event.ONTOUCHEND != event.getTypeInt()) {
					return;
				}
				
				removeHandlers();

				save();
				onEditModule.execute();
				onSave.execute();
				hide();
				resetList();
				saveViewRendered();
				restore();
				
				if (moduleChangedListener != null) {
					moduleChangedListener.onModuleChanged();
				}
				$("#content").off("mousedown touchstart");
			}
		});
		
		Event.sinkEvents(apply, Event.ONCLICK);
		Event.setEventListener(apply, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				save();
				onEditModule.execute();
				onSave.execute();
				resetList();
				saveViewRendered();
				restore();
				
				if (moduleChangedListener != null) {
					moduleChangedListener.onModuleChanged();
				}
			}
		});
		
		
		Event.sinkEvents(closeButton, Event.ONCLICK);
		Event.setEventListener(closeButton, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				if(isModified() && MainPageUtils.isWindowOpened("staticListPage")) {
					saveChanges(true);
				} else if (MainPageUtils.isWindowOpened("staticListPage")) {
					hide();
					resetList();
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
					
					for(StaticListItemWidget list : items) {
						HTMLListItemWidget item = list.getListHTMLItem();
						item.setValue(GapsParserUtil.render((item.getValue())));
					}
					restore();
				} else {
					isRenderMode = false;
					for(int i = 0; i < items.size(); i++) {
						HTMLListItemWidget item = items.get(i).getListHTMLItem();
						item.setValue(unwrapGaps(i));
					}
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
	
	public native String unwrapGaps(int index) /*-{
		function replaceWithGapDef(items) {
			$_.each(items, function(i, el) {
				$_(el).replaceWith($_(el).attr("data-gap-value"));
			});	
		}
		
		var syntax = "",
			$_ = $wnd.$,
			el = $_(".propertiesItem-Value").find("iframe")[index],
			clone = $_(el).contents().clone(),
			items = clone.find("input[data-gap]");
			link_items = clone.find("a[data-gap]");
		
		replaceWithGapDef(items);
		replaceWithGapDef(link_items);
		
		return clone.find('body').html();
	}-*/;
	
	private void addHandler() {	
		$(".propertiesItem-Value").find("iframe").each(new Function() {
			public void f(Element e) {
				GQuery iframeContent = $(e).contents();
				
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
		});
	}
	
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
				String definition = "<input size='" + (widget.getDefinition().length() - 6) + "' data-gap='editable' data-gap-value='" +widget.getDefinition() +"' readonly></input>";
				
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
		
	private native void insert(String html, JavaScriptObject selectionRange) /*-{
		var selection, range;
	
		if (selectionRange) {
	    	selection = $wnd.$(".propertiesItem-Value").find("iframe")[0].contentWindow.getSelection();
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
	            var doc = $wnd.$(".propertiesItem-Value").find("iframe")[0].contentWindow.document,
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
	
	private void insertHTML(String html, JavaScriptObject selectionRange) {
		if (NavigatorUtil.isIEBrowser()) {
			insert(html, selectionRange);
		} else {
			toolbar.textFormatter.insertHTML(html);
		}
	}
	
	private native String getSelection() /*-{		
		var $iframes = $wnd.$(".propertiesItemsList").find("iframe");
		for(var i=0; i<$iframes.size();i++){
			var selection = $iframes[i].contentWindow.getSelection().toString();
			if(selection!==null && selection!==undefined && selection.length>0) {
				return selection;
			}
		}
		return "";
	}-*/;
	
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
				String definition = "<input size='" + Math.max(widget.getAnswerSize(), widget.getPlaceholder().length()) +"' data-gap='filled' placeholder='"
				+ widget.getPlaceholder() +"' data-gap-value='" +widget.getDefinition() +"' readonly></input>";

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
		
		MainPageUtils.getModals().addDropDownGapWidget("ItemsEditor", mode, values, new QuestionModalListener() {
			@Override
			public void onDecline() {
				restore();
			}
			
			@Override
			public void onAccept() {
				DropDownGapWidget widget = MainPageUtils.getModals().getDropDownGapWidget();
				String definition = "<input value='&#9660;' style='text-align: right; width: 80px'  data-gap='dropdown' data-gap-value='" +widget.getDefinition() +"'></input>";

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
	
	private native void addStyles() /*-{
	    $wnd.$(".propertiesItem-Value").find("iframe").contents().find("input[data-gap]").css({"cursor": "pointer"});
	}-*/;
	
	private void restore() {
		addHandler();
		addStyles();
	}
	
	private native void addSelectStyle() /*-{
	    $wnd.$(".propertiesItem-Value").find("iframe").contents().find("body").css({"-ms-user-select": "text"});
	}-*/;
	
	private void updateView() {
		final GQuery content = $(".propertiesItem-Value").find("iframe").contents().find("body");
	
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
	
	private void insertGap(String selectedOption) {
		if (selectedOption.equals("editable")) {
			addSingleGapWidget(null, null);
		} else if (selectedOption.equals("filled")) {
			addSingleFilledGapWidget(null, null);
		} else if (selectedOption.equals("dropdown")) {
			addDropDownGapWidget(null, null);
		}
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onSave = actionFactory.getAction(ActionType.save);
		onEditModule = actionFactory.getAction(ActionType.editModule);
		onModalOpened = (ModalOpenedAction) actionFactory.getAction(ActionType.modalOpened);
	}
	
	private void saveChanges(boolean usePrompt) {
		if (!usePrompt) {
			save();
			saveViewRendered();
		} else {
			getModals().addModal(DictionaryWrapper.get("save_changes"), new QuestionModalListener() {
				@Override
				public void onDecline() {
					removeHandlers();
					hide();
				}
				
				@Override
				public void onAccept() {
					removeHandlers();
					save();
					saveViewRendered();
					hide();
				}
			});
		}
	}

	private boolean isModified() {
		for (StaticListItemWidget item : items) {
			if (item.isModified()) {
				return true;
			}
		}

		return false;
	}
	
	public void hide() {
		removeHandlers();

		resetList();
		WidgetLockerController.hide();
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}

	public void show() {
		MainPageUtils.show(panel);

		
		$("#content").on("mousedown", new Function(){
			public void f() {
				if(isModified() && MainPageUtils.isWindowOpened("staticListPage")) {
					saveChanges(true);
				} else if (MainPageUtils.isWindowOpened("staticListPage")) {
					hide();
					resetList();
				}
			}
		});
		
		resetList();
		
		if (addGap.renderedOption.isChecked()) {
			isRenderMode = true;
			Timer t = new Timer() {
			  public void run() {
			    restore();
			  }
			};
				
			t.schedule(100);
		} else {
			isRenderMode = false;
		}

		if (!isInitialized) {
			updateView();
			isInitialized = true;
		}
		
		addGap.setVisible(toolbar.isVisible());
	}
	
	// Set all properties their initial values.
	// It's necessary to check if any property was changed
	private void resetList() {
		if (items == null) return;
		
		for(StaticListItemWidget item : items) {
			item.resetAllItems();
		}
	}
	
	public void clear() {
		items.clear();
		list.clear();
	}
	
	private void save() {
		for (StaticListItemWidget item : items) {
			item.save();
		}
	}
	
	private void addItems(int itemsCount) {
		this.property.addChildren(itemsCount);
		
		renderView();
		save();
	}

	public void setProperty(IStaticListProperty property) {
		this.property = property;
		renderView();
	}
	
	private void renderView() {
		clear();
		
		int childrenCount = property.getChildrenCount();
		for (int i = 0; i < childrenCount; i++) {
		IPropertyProvider propertyProvider = property.getChild(i);
			// It's critical for property provider to be set after file selector and toolbar!
			for (int j = 0; j < propertyProvider.getPropertyCount(); j++) {
				StaticListItemWidget item = new StaticListItemWidget();
				item.setName(propertyProvider.getProperty(j).getDisplayName());
				item.setFileSelector(fileSelector);
				item.setToolbar(toolbar);
				item.setPropertyProvider(propertyProvider, j);

				final int itemIndex = i;
				item.setListener(new ListItemEventListener() {
					@Override
					public void onRemove() {
						//none
					}
					
					@Override
					public void onMoveUp() {
						moveItemUp(itemIndex);
					}
					
					@Override
					public void onMoveDown() {
						moveItemDown(itemIndex);
					}
				});
				
				if (i == 0) {
					item.setArrowUpDisabled();
				}
				
				if (i == childrenCount - 1) {
					item.setArrowDownDisabled();
				}
	
				items.add(item);
				list.add(item);
			}
			
		}
		
		resetList();
		MainPageUtils.updateScrollbars();
		determineToolbarVisibility();
	}
	
	private static native void  determineToolbarVisibility() /*-{
		if (typeof $wnd.iceDetermineHTMLToolbarVisibilityInStaticList == 'function') {
			$wnd.iceDetermineHTMLToolbarVisibilityInStaticList();
		}
	}-*/;
		
	private void moveItemUp(int index) {
		if (index < 1) {
			return;
		}
		
		save();
		property.moveChildUp(index);
		save();
		renderView();
		onEditModule.execute();
		onSave.execute();
		
		if (moduleChangedListener != null) {
			moduleChangedListener.onModuleChanged();
		}
	}

	private void moveItemDown(int index) {
		if (index >= property.getChildrenCount() - 1) {
			return;
		}
		
		save();
		property.moveChildDown(index);
		save();
		renderView();
		onEditModule.execute();
		onSave.execute();
		
		if (moduleChangedListener != null) {
			moduleChangedListener.onModuleChanged();
		}
	}
	
	public void updateElementsTexts() {
		title.setInnerText(DictionaryWrapper.get("items_editor"));
		apply.setInnerText(DictionaryWrapper.get("apply"));
		save.setInnerText(DictionaryWrapper.get("save"));
	
	}

	public void setFileSelector(FileSelectorWidget fileSelector) {
		this.fileSelector = fileSelector;
		this.toolbar.setFileSelector(fileSelector);
	}
	
	public void setModuleChangedListener(ModuleChangedListener listener) {
		this.moduleChangedListener = listener;
	}

	public void setModals(ModalsWidget modals) {
		this.modals = modals;
	}
	
	private ModalsWidget getModals() {
		return modals;
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

	@Override
	public boolean getRenderOption() {
		return this.addGap.isChecked();
	}

	@Override
	public void changeRenderOption() {
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
}
