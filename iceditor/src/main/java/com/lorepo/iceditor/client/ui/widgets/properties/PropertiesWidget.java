package com.lorepo.iceditor.client.ui.widgets.properties;

import static com.google.gwt.query.client.GQuery.$;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.DivElement;
import com.google.gwt.dom.client.SpanElement;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.CopyPageLayoutAction;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.EditModuleMainPropertiesAction;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.layoutsCopier.LayoutsCopier;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.layoutsCopier.LayoutsList.LayoutsListListener;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.propertiesWidget.PropertiesPanelSemiResponsiveLayoutsChanger;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.docs.DocViewerWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.ConnectorBlocksEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorEventListener;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.HTMLEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.ItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.LayoutEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.StaticItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.TextEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.iceditor.client.ui.widgets.utils.PresentationUtils;
import com.lorepo.icf.properties.IAudioProperty;
import com.lorepo.icf.properties.IConnectorBlocksProperty;
import com.lorepo.icf.properties.IBooleanProperty;
import com.lorepo.icf.properties.IEnumSetProperty;
import com.lorepo.icf.properties.IEventProperty;
import com.lorepo.icf.properties.IFileProperty;
import com.lorepo.icf.properties.IHtmlProperty;
import com.lorepo.icf.properties.IImageProperty;
import com.lorepo.icf.properties.IListProperty;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyListener;
import com.lorepo.icf.properties.IPropertyProvider;
import com.lorepo.icf.properties.IStaticListProperty;
import com.lorepo.icf.properties.IStringListProperty;
import com.lorepo.icf.properties.ITextProperty;
import com.lorepo.icf.properties.IVideoProperty;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icf.widgets.mediabrowser.IMediaProvider.MediaType;
import com.lorepo.icplayer.client.addonsLoader.AddonLoaderFactory;
import com.lorepo.icplayer.client.addonsLoader.IAddonLoader;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonDescriptorFactory;
import com.lorepo.icplayer.client.model.addon.AddonProperty;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.ILayoutProperty;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IChapter;

public class PropertiesWidget extends Composite {

	private static PropertiesWidgetUiBinder uiBinder = GWT.create(PropertiesWidgetUiBinder.class);

	interface PropertiesWidgetUiBinder extends UiBinder<Widget, PropertiesWidget> {}

	@UiField SpanElement nodeName;
	@UiField HTMLPanel propertiesList;
	@UiField DivElement title;

	@UiField AnchorElement moduleDoc;
	
    private final String HIDDEN_SEMI_RESPONSIVE_CONTAINER = "properties-panel-semi-responsive-container-hidden";
    private final String VISIBLE_SEMI_RESPONSIVE_CONTAINER = "semi-responsive-layouts-editing-form";

	private AbstractAction onModuleEdit;
	private EditModuleMainPropertiesAction onModulePositionEdit;
	private AbstractAction onPageEdit;
	private AbstractAction onChapterEdit;
	private AbstractAction onSave;
	private CopyPageLayoutAction onCopyLayout;

	
	private final Map<String, Composite> modulePropertiesWidgets = new HashMap<String, Composite>();
	private final Map<String, Widget> pagePropertiesWidgets = new HashMap<String, Widget>();

	private IModuleModel module;
	private ModuleChangedListener moduleChangedListener;

	private TextEditorWidget textEditor;
	private BlocksEditorWidget blocksEditor;
	private HTMLEditorWidget htmlEditor;
	private ItemsEditorWidget itemsEditor;
	private StaticItemsEditorWidget staticItemsEditor;
	private final HashMap<String, String> properties = new HashMap<String, String>();
	private LinkedHashMap<String, String> headerOptions = new LinkedHashMap<String, String>();
	private LinkedHashMap<String, String> footerOptions = new LinkedHashMap<String, String>();
	private FileSelectorWidget fileSelector;
	private LayoutEditorWidget layoutEditor;
	private AddonProperty defaultAddonProperty;
	private AppFrame appFrame;
	private DocViewerWidget docViewer;
	private Content content;
	private int actualActionId = 0;
	private Page currentPage;
	
	PropertiesPanelSemiResponsiveLayoutsChanger layoutsChanger = new PropertiesPanelSemiResponsiveLayoutsChanger();
	LayoutsCopier layoutsCopier = new LayoutsCopier();
	
	IPropertyListener layoutPropertyListener = new IPropertyListener() {
		@Override
		public void onPropertyChanged(IProperty source) {
			if (source instanceof ILayoutProperty) {
				updatePanelProperty(module, actualActionId);
			}
		}
	};
	public PropertiesWidget() {
		this.initWidget(uiBinder.createAndBindUi(this));

		this.nodeName.setId("moduleTypeName");
		this.propertiesList.getElement().setId("propertiesList");
		this.moduleDoc.setId("moduleDoc");
		this.updateElementsTexts();
		this.connectModuleDocEvents();
		this.layoutsCopier.setListener(new LayoutsListListener() {
			
			@Override
			public void onChange(String layoutID) {
				onCopyLayout.execute(layoutID);
			}
		});
	}

	private void connectModuleDocEvents() {
		Event.sinkEvents(this.moduleDoc, Event.ONCLICK);
		Event.setEventListener(this.moduleDoc, new EventListener() {

			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONCLICK == event.getTypeInt()) {
					if (PropertiesWidget.this.module != null) {
						PropertiesWidget.this.docViewer.show(PropertiesWidget.this.module);
					} else {
						PropertiesWidget.this.docViewer.show(PropertiesWidget.this.currentPage);
					}
				}
			}
		});
	}

	public void setAppFrame(AppFrame appFrame) {
		this.appFrame = appFrame;
	}

	public void setContent(Content content) {
		this.content = content;
		this.layoutsChanger.setSemiResponsiveLayouts(this.content.getActualSemiResponsiveLayouts());
		this.layoutsCopier.setLayouts(this.content.getActualSemiResponsiveLayouts());
	}
	

	public void setSelectedSemiResponsiveLayoutView(String semiResponsiveLayoutID) {
		this.layoutsChanger.setSelectedSemiResponsiveLayoutID(semiResponsiveLayoutID);
	}

	public int getMaxScore() {
		return this.appFrame.getPresentation().getPageMaxScore();
	}

	private void addPageProperties(final Page page, int actionId) {
		if (actionId < this.actualActionId){
			return;
		}
		this.actualActionId++;

		this.pagePropertiesWidgets.clear();
		Widget propertyWidget = null;
		boolean isCustomWeight = false;
		
		this.propertiesList.add(this.layoutsChanger);
		this.propertiesList.add(this.layoutsCopier);
		
		for (int i = 0; i < page.getPropertyCount(); i++) {
			final IProperty property = page.getProperty(i);
			String propertyName = this.getPropertyName(property);

			if (property.getName().equals(DictionaryWrapper.get("page_preview"))) {
				final ButtonPropertyWidget preview = new ButtonPropertyBuilder(DictionaryWrapper.get("page_preview")).
						text(property.getValue()).
						build();

				preview.setListener(new ButtonPropertyClickListener() {
					@Override
					public void onSelected() {
						PropertiesWidget.this.fileSelector.setMediaType(MediaType.IMAGE);
						PropertiesWidget.this.fileSelector.setShouldCloseWidgetLocker(true);
						PropertiesWidget.this.fileSelector.setListener(new FileSelectorEventListener() {
							@Override
							public void onSelected(String filePath) {
								PropertiesWidget.this.fileSelector.hide();
								preview.setText(filePath);
								page.setPreview(filePath);
								PropertiesWidget.this.onSave.execute();
							}
						});

						PropertiesWidget.this.fileSelector.show();
					}
				});

				propertyWidget = preview;
			} else if (property instanceof IBooleanProperty) {
				propertyWidget = new BooleanPropertyBuilder(propertyName, property.getValue().equals("True")).
					listener(new BooleanPropertyChangeListener() {
						@Override
						public void onChange(boolean selected) {
							property.setValue(selected ? "True" : "False");
							PropertiesWidget.this.onPageEdit.execute();
						}
					}).build();
			} else if (property instanceof IEnumSetProperty) {
				IEnumSetProperty enumProperty = (IEnumSetProperty) property;
				String[] options = new String[enumProperty.getAllowedValueCount()];
				for (int j = 0; j < options.length; j++) {
					options[j] = enumProperty.getAllowedValue(j);
				}

				propertyWidget = new SelectPropertyBuilder(propertyName, options).
					listener(new SelectPropertyChangeListener() {
						@Override
						public void onChange(String value) {
							if (property.getName().equals(DictionaryWrapper.get("weight_mode"))) {
								final Widget customMaxScore = PropertiesWidget.this.pagePropertiesWidgets.get(DictionaryWrapper.get("weight_value"));
								customMaxScore.setVisible(value.equals("custom"));
								if (value == "maxPageScore") {
									page.setPageMaxScore(PropertiesWidget.this.getMaxScore());
								} else if (value == "custom") {
									page.setPageMaxScore(page.getPageCustomWeight());
								} else { // default
									page.setPageMaxScore(1);
								}
							}

							property.setValue(value);
							PropertiesWidget.this.onPageEdit.execute();
						}
					}).
					selected(enumProperty.getValue()).build();

				if (property.getName().equals(DictionaryWrapper.get("weight_mode"))) {
					isCustomWeight = enumProperty.getValue().equals("custom");
				}
			} else if (property instanceof IFileProperty) {
				propertyWidget = new ButtonPropertyBuilder(propertyName).text(property.getValue()).build();
			} else {
				propertyWidget = new StringPropertyBuilder(propertyName, property.getValue()).build();
				final StringPropertyWidget stringPropertyWidget = (StringPropertyWidget) propertyWidget;
				stringPropertyWidget.setListener(new StringPropertyChangeListener() {
					@Override
					public void onChange(String value) {
						property.setValue(value);
						PropertiesWidget.this.nodeName.setInnerText(page.getName());
						PropertiesWidget.this.onPageEdit.execute();

						if (property.getName().equals(DictionaryWrapper.get("weight_value"))) {
							if (isNumeric(value)) {
								int roundedValue = (int) Math.round(Double.parseDouble(value));
								if (roundedValue < 1) {
									page.setPageCustomWeight(1);
									value = Integer.toString(1);
								} else {
									page.setPageCustomWeight(roundedValue);
									value = Integer.toString(roundedValue);
								}
							}

							property.setValue(value);
							stringPropertyWidget.setValue(property.getValue());
						}
					}
				});

				if (property.getName().equals(DictionaryWrapper.get("weight_value")) && !isCustomWeight) {
					propertyWidget.setVisible(false);
				}
			}

			if (propertyWidget != null) {
				this.propertiesList.add(propertyWidget);
				this.pagePropertiesWidgets.put(property.getName(), propertyWidget);
			}
		}
		MainPageUtils.updateWidgetScrollbars("properties");
	}

	public boolean isModuleSet() {
		return this.module != null;
	}
	
	public void setPage(Page page) {
		int localActionId = this.actualActionId;
		this.removeLayoutListener();

		this.module = null;
		this.nodeName.setInnerText(page.getName());

		this.clearPropertiesListView();

		this.currentPage = page;
		this.currentPage.setModulesMaxScore(this.getMaxScore());

		this.addPageProperties(page,localActionId);
		if (content.getCommonPageById(page.getId()) == null) {
			this.addHeadersFootersList();
		}
		this.showModuleDoc();
	}

	public void setModule(final IModuleModel module) {
		int actualAction = this.actualActionId;
		if (this.module != null && this.module.getId().equals(module.getId())) {
			return;
		}
		this.docViewer.hide();
		this.removeLayoutListener();

		this.module = module;

		this.module.addPropertyListener(this.layoutPropertyListener);

		this.nodeName.setInnerText(module.getProviderName());
		this.clearPropertiesListView();

		this.updatePanelProperty(module,actualAction);
		this.showModuleDoc();

		this.htmlEditor.setModuleName(module.getModuleTypeName());
	}
	
	public void setGroup(Group group) {
		this.removeLayoutListener();

		this.module = null;

		this.clearPropertiesListView();
		this.nodeName.setInnerText(group.getProviderName());

		this.addGroupProperties(group);
		this.hideModuleDoc();
	}

	public void setProperties(IPropertyProvider finalModule, AddonDescriptor descriptor, int actionId) {
		for(int i = 0; i < finalModule.getPropertyCount(); i++){
			for(AddonProperty property: descriptor.getProperties()){
				if (finalModule.getProperty(i).getName().equals(property.getName())) {
					this.properties.put(finalModule.getProperty(i).getName(), property.getDisplayName());
					if (property.isDefault()) {
						this.defaultAddonProperty = property;
					}
				}
			}
		}

		this.addModuleProperties((IModuleModel) finalModule,actionId);
	}
	
	public String getSelectedLayoutId() {
		return layoutsChanger.getSelectedSemiResponsiveLayoutID();
	}

	public  LayoutsCopier getLayoutsCopier() {
		return this.layoutsCopier;
	}

	private boolean isAddon(String name) {
		if(AddonDescriptorFactory.getInstance().getEntry(name) != null) {
			return true;
		}
		return false;
	}
	
	public void updatePanelProperty(final IPropertyProvider module, final int actionId) {
		final IPropertyProvider finalModule = module;
		final HashMap<String, AddonDescriptor> addonDescriptors = this.content.getAddonDescriptors();
		
		if(this.content.addonIsLoaded(finalModule.getProviderName())) {
			this.setProperties(finalModule, addonDescriptors.get(finalModule.getProviderName()), actionId);
		} else if(this.isAddon(finalModule.getProviderName())) {
			AddonLoaderFactory addonLoaderFactory = new AddonLoaderFactory(this.content.getBaseUrl());
			IAddonLoader loader = addonLoaderFactory.getAddonLoader(addonDescriptors.get(finalModule.getProviderName()));
			loader.load(new ILoadListener() {
				@Override
				public void onFinishedLoading(Object obj) {
					if (actionId >= PropertiesWidget.this.actualActionId) {
					    PropertiesWidget.this.setProperties(finalModule, addonDescriptors.get(finalModule.getProviderName()), actionId);
					}
				}
				
				@Override
				public void onError(String error) {
					Window.alert(DictionaryWrapper.get("error_loading_addon") + finalModule.getProviderName());
				}
			});
		} else { // set property for modules
			this.addModuleProperties((IModuleModel) module, actionId);
		}
	}

	public void setActionFactory(ActionFactory actionFactory) {
		this.onModuleEdit = actionFactory.getAction(ActionType.editModule);
		this.onModulePositionEdit = (EditModuleMainPropertiesAction) actionFactory.getAction(ActionType.editModulePosition);
 		this.onPageEdit = actionFactory.getAction(ActionType.editPage);
		this.onChapterEdit = actionFactory.getAction(ActionType.editChapter);
		this.onSave = actionFactory.getAction(ActionType.save);
		this.onCopyLayout = (CopyPageLayoutAction) actionFactory.getAction(ActionType.copyPageLayout);
		
		layoutsChanger.setActionFactory(actionFactory);
	}

	private void addSeparator() {
		this.propertiesList.add(new PropertiesSeparatorWidget());
	}

	private void addGroupProperties(final Group group) {
		group.addPropertyMaxScore();
		this.modulePropertiesWidgets.clear();

		int propertyCount = group.getPropertyCount();
		boolean isDefaultScoring = false;
		boolean isMinusErrorScoring = false;

		for (int i = 0; i < propertyCount; i++) {
			final IProperty property = group.getProperty(i);
			final String propertyName = this.getPropertyName(property);
			Composite propertyWidget;
			if (property instanceof IEnumSetProperty) {
				IEnumSetProperty enumProperty = (IEnumSetProperty) property;
				String[] options = new String[enumProperty.getAllowedValueCount()];
				for (int j = 0; j < options.length; j++) {
					options[j] = enumProperty.getAllowedValue(j);
				}
				propertyWidget = new SelectPropertyBuilder(propertyName, options).
						listener(new SelectPropertyChangeListener() {
							@Override
							public void onChange(String value) {
								boolean isDefault = value.equals(DictionaryWrapper.get("defaultScore"));
								boolean isMinus = value.equals(DictionaryWrapper.get("minusErrors"));
								PropertiesWidget.this.propertiesList.getWidget(2).setVisible(!(isDefault || isMinus));
								property.setValue(value);
							}
						}).
						selected(enumProperty.getValue()).build();

				if (enumProperty.getValue().equals(DictionaryWrapper.get("defaultScore"))) {
					isDefaultScoring = true;
				}
				
				if (enumProperty.getValue().equals(DictionaryWrapper.get("minusErrors"))) {
					isMinusErrorScoring = true;
				}

				this.propertiesList.add(propertyWidget);
				
			} else if (property instanceof IBooleanProperty) {
				propertyWidget = new BooleanPropertyBuilder(propertyName, property.getValue().equals("True")).
						listener(new BooleanPropertyChangeListener() {
							@Override
							public void onChange(boolean selected) {
								property.setValue(selected ? "True" : "False");
								PropertiesWidget.this.onModuleEdit.execute();
								if (PropertiesWidget.this.moduleChangedListener != null) {
									PropertiesWidget.this.moduleChangedListener.onModuleChanged();
								}
							}
						}).build();	
				this.propertiesList.add(propertyWidget);
			} else {
				propertyWidget = new StringPropertyBuilder(propertyName, property.getValue()).
						listener(new StringPropertyChangeListener() {
							@Override
							public void onChange(String value) {
								if(isNumeric(value) && PropertiesWidget.this.isMainProperty(property.getName())) {
									int roundedValue = (int) Math.round(Double.parseDouble(value));
									value = Integer.toString(roundedValue);
								}

								if(PropertiesWidget.this.isNumberProperty(property.getName()) && !isNumeric(value)) {
									value = "";
								}
								
								property.setValue(value);
								PropertiesWidget.this.onModuleEdit.execute();
								if (PropertiesWidget.this.moduleChangedListener != null) {
									PropertiesWidget.this.moduleChangedListener.onModuleChanged();
								}
							}
						}).build();

				if (property.getName().equals(DictionaryWrapper.get("max_score")) && (isDefaultScoring || isMinusErrorScoring)) {
					propertyWidget.setVisible(false);
				}

				this.propertiesList.add(propertyWidget);
			}
		}

		MainPageUtils.updateWidgetScrollbars("properties");
	}

	private void showHTMLEditor(final IProperty property) {
		//prevent before multi-opening
		if(MainPageUtils.isWindowOpened("htmlEditorPage")) {
			return;
		}
		this.htmlEditor.setText(property.getValue());
		this.htmlEditor.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				property.setValue(PropertiesWidget.this.htmlEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.htmlEditor.hide();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}

			@Override
			public void onApply() {
				property.setValue(PropertiesWidget.this.htmlEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.onSave.execute();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}
		});
		this.htmlEditor.show();
	}

	private void showTextEditor(final IProperty property, String editorName) {
		this.textEditor.setName(editorName);
		this.textEditor.setText(property.getValue());
		this.textEditor.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				property.setValue(PropertiesWidget.this.textEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.textEditor.hide();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}

			@Override
			public void onApply() {
				property.setValue(PropertiesWidget.this.textEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.onSave.execute();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}
		});
		this.textEditor.show();
	}
	
	private void showBlocksEditor(final IProperty property, String editorName) {
		this.blocksEditor.setName(editorName);
		this.blocksEditor.setText(property.getValue());
		this.blocksEditor.setListener(new MainPageEventListener() {
			@Override
			public void onSave() {
				property.setValue(PropertiesWidget.this.blocksEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.blocksEditor.hide();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}

			@Override
			public void onApply() {
				property.setValue(PropertiesWidget.this.blocksEditor.getText());
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.onSave.execute();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}
		});
		this.blocksEditor.show();
	}

	private void showImageEditor(final IProperty property) {
		final IProperty fileProperty = property;

		this.fileSelector.setMediaType(MediaType.IMAGE);
		this.fileSelector.setShouldCloseWidgetLocker(true);
		this.fileSelector.setListener(new FileSelectorEventListener() {
			@Override
			public void onSelected(String filePath) {
				fileProperty.setValue(filePath);
				PropertiesWidget.this.onModuleEdit.execute();
				PropertiesWidget.this.fileSelector.hide();

				if (PropertiesWidget.this.moduleChangedListener != null) {
					PropertiesWidget.this.moduleChangedListener.onModuleChanged();
				}
			}
		});

		this.fileSelector.show();
	}

	public void showModuleDefaultPropertyEditor(final IModuleModel module) {
		if(this.isAddon(module.getProviderName())) {
			this.showDefaultEditorForAddon(module);
		} else {
			this.showDefaultEditorForModule(module);			
		}
	}
	
	private void showDefaultEditorForAddon(final IModuleModel module) {
		AddonDescriptor addonDescriptor = (AddonDescriptor) this.content.getAddonDescriptor(module.getProviderName());
		
		AddonProperty defaultProperty = addonDescriptor.getDefaultProperty();
		
		if (defaultProperty != null) {
			this.showEditorBasedOnPropertyType(defaultProperty, module);
		}
	}

	private void showEditorBasedOnPropertyType(AddonProperty descriptorProperty, IModuleModel module) {
		String type = descriptorProperty.getType();
		IProperty moduleProperty = this.getModuleProperty(descriptorProperty, module);
		
		if (moduleProperty != null) {
			if(type.compareTo("text") == 0) {
				this.showTextEditor(moduleProperty, DictionaryWrapper.get("text_editor"));
			} else if(type.compareTo("list") == 0) {
				this.showItemsEditor(moduleProperty, module.getModuleName());
			} else if(type.compareTo("staticlist") == 0) {
				this.showStaticItemsEditor(moduleProperty);
			}else if(type.compareTo("image") == 0) {
				this.showImageEditor(moduleProperty);
			} else if(type.compareTo("html") == 0) {
				this.showHTMLEditor(moduleProperty);
			} else if(type.compareTo("event") == 0) {
				this.showTextEditor(moduleProperty, DictionaryWrapper.get("event_editor"));
			} else if(type.compareTo("connectorblocks") == 0) {
				this.showBlocksEditor(moduleProperty, DictionaryWrapper.get("code_blocks_editor"));
			}
		}
	}
	
	private IProperty getModuleProperty(AddonProperty property, IModuleModel module) {
		int propertyCount = module.getPropertyCount();
		for (int i = 0; i < propertyCount; i++) {
			IProperty moduleProperty = module.getProperty(i);
			if (moduleProperty.getName().compareTo(property.getName()) == 0) {
				return moduleProperty;
			}
		}
		
		return null;
	}
	
	private void showDefaultEditorForModule(final IModuleModel module) {
		int propertyCount = module.getPropertyCount();
		String moduleName = module.getModuleTypeName();
		
		for (int i = 0; i < propertyCount; i++) {
			final IProperty property = module.getProperty(i);
			if (property.isDefault()) {
				if (moduleName.equals("Text")) {
					this.showHTMLEditor(property);
				} else if (moduleName.equals("Image")) {
					this.showImageEditor(property);
				} else if (moduleName.equals("Choice")) {
					this.showItemsEditor(property, module.getModuleName());
				} else if (moduleName.equals("Source list")) {
					this.showTextEditor(property, DictionaryWrapper.get("string_list_editor"));
				} else if (moduleName.equals("Ordering")) {
					this.showItemsEditor(property, module.getModuleName());
				} else if (moduleName.equals("Image gap")) {
					this.showTextEditor(property, DictionaryWrapper.get("string_list_editor"));
				} else if (moduleName.equals("Image_Identification")) {
					this.showImageEditor(property);
				} else if (moduleName.equals("Image source")) {
					this.showImageEditor(property);
				}
			}
		}
	}
	
	private void showItemsEditor(final IProperty property, final String moduleName) {
		final IListProperty listProperty = (IListProperty) property;

		this.itemsEditor.clear();
		this.itemsEditor.setProperty(listProperty, moduleName);
		this.itemsEditor.show();
	}
	
	private void showStaticItemsEditor(final IProperty property) {
		final IStaticListProperty listProperty = (IStaticListProperty) property;

		this.staticItemsEditor.clear();
		this.staticItemsEditor.setProperty(listProperty);
		this.staticItemsEditor.show();
	}
	
	private void addModuleProperties(final IModuleModel module, int actionId) {
		if (actionId != this.actualActionId) {
			return;
		}
		this.actualActionId++;
		this.modulePropertiesWidgets.clear();

		int propertyCount = module.getPropertyCount();

		for (int i = 0; i < propertyCount; i++) {
			final IProperty property = module.getProperty(i);
			String propertyDisplayName = property.getDisplayName();
			String propertyName = property.getName();

			if (propertyDisplayName == null || propertyDisplayName.isEmpty()) {
				propertyDisplayName = propertyName;
			}

			if (this.properties != null && this.properties.get(propertyName) != null && !this.properties.get(propertyName).isEmpty()) {
				propertyDisplayName = this.properties.get(propertyName);
			}

			Composite propertyWidget;

			if (property instanceof ILayoutProperty) {
				propertyWidget = this.createLayoutPropertyWidget(property, propertyDisplayName);
			} else if (property instanceof IAudioProperty) {
				propertyWidget = this.createFilePropertyWidget(property, propertyDisplayName, MediaType.AUDIO);
			} else if (property instanceof IBooleanProperty) {
				propertyWidget = new BooleanPropertyBuilder(propertyDisplayName, property.getValue().equals("True")).
						listener(new BooleanPropertyChangeListener() {
							@Override
							public void onChange(boolean selected) {
								property.setValue(selected ? "True" : "False");
								PropertiesWidget.this.onModuleEdit.execute();
								if (PropertiesWidget.this.moduleChangedListener != null) {
									PropertiesWidget.this.moduleChangedListener.onModuleChanged();
								}
							}
						}).build();
			} else if (property instanceof IEnumSetProperty) {
				IEnumSetProperty enumProperty = (IEnumSetProperty) property;
				String[] options = new String[enumProperty.getAllowedValueCount()];
				for (int j = 0; j < options.length; j++) {
					options[j] = enumProperty.getAllowedValue(j);
				}
				propertyWidget = new SelectPropertyBuilder(propertyDisplayName, options).
						listener(new SelectPropertyChangeListener() {
							@Override
							public void onChange(String value) {
								property.setValue(value);
								PropertiesWidget.this.onModuleEdit.execute();
								if (PropertiesWidget.this.moduleChangedListener != null) {
									PropertiesWidget.this.moduleChangedListener.onModuleChanged();
								}
							}
						}).
						selected(enumProperty.getValue()).build();
			} else if (property instanceof IEventProperty) {
				propertyWidget = this.createTextPropertyWidget(property, propertyDisplayName, DictionaryWrapper.get("event_editor"));
			} else if (property instanceof IFileProperty) {
				propertyWidget = this.createFilePropertyWidget(property, propertyDisplayName, MediaType.FILE);
			} else if (property instanceof IHtmlProperty) {
				propertyWidget = this.createHTMLPropertyWidget(property, propertyDisplayName);
			} else if (property instanceof IImageProperty) {
				propertyWidget = this.createFilePropertyWidget(property, propertyDisplayName, MediaType.IMAGE);
			} else if (property instanceof IListProperty) {
				propertyWidget = this.createListPropertyWidget(property, propertyDisplayName, module.getModuleName());
			} else if (property instanceof IStaticListProperty) {
				propertyWidget = this.createStaticListPropertyWidget(property, propertyDisplayName);
			} else if (property instanceof IStringListProperty) {
				propertyWidget = this.createTextPropertyWidget(property, propertyDisplayName, DictionaryWrapper.get("string_list_editor"));
			} else if (property instanceof ITextProperty) {
				propertyWidget = this.createTextPropertyWidget(property, propertyDisplayName, DictionaryWrapper.get("text_editor"));
			} else if (property instanceof IConnectorBlocksProperty) {
				propertyWidget = this.createBlocksPropertyWidget(property, propertyDisplayName, DictionaryWrapper.get("code_blocks_editor"));
			} else if (property instanceof IVideoProperty) {
				propertyWidget = this.createFilePropertyWidget(property, propertyDisplayName, MediaType.VIDEO);
			} else {
				propertyWidget = new StringPropertyBuilder(propertyDisplayName, property.getValue()).build();
				final StringPropertyWidget stringPropertyWidget = (StringPropertyWidget) propertyWidget;
				stringPropertyWidget.setListener(new StringPropertyChangeListener() {
					@Override
					public void onChange(String value) {
						//check if string is a number and than round it
						if(isNumeric(value) && PropertiesWidget.this.isMainProperty(property.getName())){
							int roundedValue = (int) Math.round(Double.parseDouble(value));
							value = Integer.toString(roundedValue);
						}

						if(PropertiesWidget.this.isNumberProperty(property.getName()) && !isNumeric(value)){
							value = "";
						}

						property.setValue(value);
						stringPropertyWidget.setValue(property.getValue());

						if (PropertiesWidget.this.isMainProperty(property.getName())) {
							PropertiesWidget.this.onModulePositionEdit.execute(module);
						} else {
							PropertiesWidget.this.onModuleEdit.execute();
						}

						if (PropertiesWidget.this.moduleChangedListener != null) {
							PropertiesWidget.this.moduleChangedListener.onModuleChanged();
						}
					}
				});
			}

			this.modulePropertiesWidgets.put(propertyName, propertyWidget);
			this.propertiesList.add(propertyWidget);

			if (property.getName().equals("Is Tabindex Enabled") && (i + 1) < propertyCount) {
				// "Is Visible" is last property in common properties package
				this.addSeparator();
			}

			this.colourDefaultProperty(property, module);
		}

		MainPageUtils.updateWidgetScrollbars("properties");
	}

	private boolean isNumberProperty(String propertyName) {
		return (propertyName.equals("Left") || propertyName.equals("Top") || propertyName.equals("Width") || propertyName.equals("Height") || propertyName.equals("Right") || propertyName.equals("Bottom"));		
	}
	
	//Properties that demands refresh view
	private boolean isMainProperty(String propertyName) {
		return (propertyName.equals("Left") || propertyName.equals("Top") || propertyName.equals("Width") || propertyName.equals("Height") || propertyName.equals("ID"));
	}
	
	private void colourDefaultProperty(IProperty property, IModuleModel module) {
		if (this.isAddon(module.getProviderName())) {
			if(this.isAddonPropertyDefault(property.getName(), module)) {
				colourProperty(this.defaultAddonProperty.getDisplayName());
			}
		} else {
			if (property.isDefault()) {
				colourProperty(property.getDisplayName());
			}
		}
	}

	private boolean isAddonPropertyDefault(String propertyName, IModuleModel module) {
		AddonDescriptor addonDescriptor = (AddonDescriptor) this.content.getAddonDescriptor(module.getProviderName());
		List<AddonProperty> addonProperties = addonDescriptor.getProperties();
		
		if (addonProperties != null) {
			for (AddonProperty addonProperty : addonProperties) {
				if (addonProperty.getName().equals(propertyName)) {
					return addonProperty.isDefault();
				}
			}
		}

		return false;
	}

	public static boolean isNumeric(String str)  {
		try {
			Double.parseDouble(str);
		} catch (NumberFormatException nfe) {
			return false;
		}

		return true;
	}

	private static native void colourProperty(String propertyName) /*-{
		var $propertyLabel = $wnd.$("#propertiesList").find(".propertyLabel");

		$propertyLabel.each(function() {
			var $innerText = $wnd.$(this).html();
			var $this = $wnd.$(this);
		    if($innerText === propertyName) {
		    	$this.css({"color": "#9AF3B6"});
		    }
		});
	}-*/;

	private Composite createTextPropertyWidget(final IProperty property, String displayName, final String editorName) {
		return new ButtonPropertyBuilder(displayName).
			listener(new ButtonPropertyClickListener() {
				@Override
				public void onSelected() {
					PropertiesWidget.this.textEditor.setName(editorName);
					PropertiesWidget.this.textEditor.setText(property.getValue());
					PropertiesWidget.this.textEditor.setListener(new MainPageEventListener() {
						@Override
						public void onSave() {
							property.setValue(PropertiesWidget.this.textEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.textEditor.hide();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}

						@Override
						public void onApply() {
							property.setValue(PropertiesWidget.this.textEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.onSave.execute();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}
					});
					PropertiesWidget.this.textEditor.show();
				}
			}).build();
	}
	
	private Composite createBlocksPropertyWidget(final IProperty property, String displayName, final String editorName) {
		return new ButtonPropertyBuilder(displayName).
			listener(new ButtonPropertyClickListener() {
				@Override
				public void onSelected() {
					PropertiesWidget.this.blocksEditor.setName(editorName);
					PropertiesWidget.this.blocksEditor.setText(property.getValue());
					PropertiesWidget.this.blocksEditor.setListener(new MainPageEventListener() {
						@Override
						public void onSave() {
							property.setValue(PropertiesWidget.this.blocksEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.blocksEditor.hide();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}

						@Override
						public void onApply() {
							property.setValue(PropertiesWidget.this.blocksEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.onSave.execute();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}
					});
					PropertiesWidget.this.blocksEditor.show();
				}
			}).build();
	}

	private Composite createHTMLPropertyWidget(final IProperty property, String displayName) {
		return new ButtonPropertyBuilder(displayName).
			listener(new ButtonPropertyClickListener() {
				@Override
				public void onSelected() {
					PropertiesWidget.this.htmlEditor.setText(property.getValue());
					PropertiesWidget.this.htmlEditor.setListener(new MainPageEventListener() {
						@Override
						public void onSave() {
							property.setValue(PropertiesWidget.this.htmlEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.htmlEditor.hide();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}

						@Override
						public void onApply() {
							property.setValue(PropertiesWidget.this.htmlEditor.getText());
							PropertiesWidget.this.onModuleEdit.execute();
							PropertiesWidget.this.onSave.execute();

							if (PropertiesWidget.this.moduleChangedListener != null) {
								PropertiesWidget.this.moduleChangedListener.onModuleChanged();
							}
						}
					});
					PropertiesWidget.this.htmlEditor.show();
				}
			}).build();
	}

	private Composite createLayoutPropertyWidget(IProperty property, String displayName) {
		final ILayoutProperty layoutProperty = (ILayoutProperty) property;

		return new ButtonPropertyBuilder(displayName).
				listener(new ButtonPropertyClickListener() {
					@Override
					public void onSelected() {
						PropertiesWidget.this.layoutEditor.setProperty(layoutProperty);
						PropertiesWidget.this.layoutEditor.setNamesModules(PropertiesWidget.this.currentPage.getModulesList());
						PropertiesWidget.this.layoutEditor.show();
					}
				}).build();
	}

	private Composite createListPropertyWidget(IProperty property, String displayName, final String moduleName) {
		final IListProperty listProperty = (IListProperty) property;

		return new ButtonPropertyBuilder(displayName).text("" + listProperty.getChildrenCount()).
				listener(new ButtonPropertyClickListener() {
					@Override
					public void onSelected() {
						PropertiesWidget.this.itemsEditor.clear();
						PropertiesWidget.this.itemsEditor.setProperty(listProperty, moduleName);
						PropertiesWidget.this.itemsEditor.show();
					}
				}).build();
	}
	
	private Composite createStaticListPropertyWidget(IProperty property, String displayName) {
		final IStaticListProperty listProperty = (IStaticListProperty) property;
		return new ButtonPropertyBuilder(displayName).text("").
				listener(new ButtonPropertyClickListener() {
					@Override
					public void onSelected() {
						PropertiesWidget.this.staticItemsEditor.clear();
						PropertiesWidget.this.staticItemsEditor.setProperty(listProperty);
						PropertiesWidget.this.staticItemsEditor.show();
					}
				}).build();
	}
	
	private Composite createFilePropertyWidget(IProperty property, String displayName, final MediaType mediaType) {
		final IProperty fileProperty = property;

		final ButtonPropertyWidget propertyWidget = new ButtonPropertyBuilder(displayName).
				text("" + fileProperty.getValue()).
				build();

		propertyWidget.setListener(new ButtonPropertyClickListener() {
			@Override
			public void onSelected() {
				PropertiesWidget.this.fileSelector.setMediaType(mediaType);
				PropertiesWidget.this.fileSelector.setShouldCloseWidgetLocker(true);
				PropertiesWidget.this.fileSelector.setListener(new FileSelectorEventListener() {
					@Override
					public void onSelected(String filePath) {
						fileProperty.setValue(filePath);
						propertyWidget.setText(filePath);
						PropertiesWidget.this.onModuleEdit.execute();
						PropertiesWidget.this.fileSelector.hide();

						if (PropertiesWidget.this.moduleChangedListener != null) {
							PropertiesWidget.this.moduleChangedListener.onModuleChanged();
						}
					}
				});
				PropertiesWidget.this.fileSelector.show();
			}
		});

		return propertyWidget;
	}

	public void setNewPosition(String left, String top, String right, String bottom, boolean submit) {
		if (this.modulePropertiesWidgets.isEmpty()) {
			return;
		}

		if (left == null && top == null && right == null && bottom == null) {
			return;
		}

		if (left != null) {
			StringPropertyWidget leftPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Left");
			leftPropertyWidget.setValue(left);
		}

		if (top != null) {
			StringPropertyWidget topPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Top");
			topPropertyWidget.setValue(top);
		}

		if (right != null) {
			StringPropertyWidget rightPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Right");
			rightPropertyWidget.setValue(right);
		}

		if (bottom != null) {
			StringPropertyWidget bottomPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Bottom");
			bottomPropertyWidget.setValue(bottom);
		}

		if (submit) {
			if (left != null) {
				this.module.setLeft(Integer.valueOf(left));
			}

			if (top != null) {
				this.module.setTop(Integer.valueOf(top));
			}

			if (right != null) {
				this.module.setRight((Integer.valueOf(right)));
			}

			if (bottom != null) {
				this.module.setBottom((Integer.valueOf(bottom)));
			}

			if (this.moduleChangedListener != null) {
				this.moduleChangedListener.onModuleChanged();
			}
		}
	}

	public void setNewDimensions(String height, String width, boolean submit) {
		if (this.modulePropertiesWidgets.isEmpty()) {
			return;
		}

		if (width == null && height == null) {
			return;
		}

		//if some value: width or height is null, it should be set from layout
		if (width != null) {
			StringPropertyWidget widthPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Width");
			widthPropertyWidget.setValue(width);
		}

		if (height != null) {
			StringPropertyWidget heightPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Height");
			heightPropertyWidget.setValue(height);
		}

		if (submit) {
			if (width != null) {
				this.module.setWidth(Integer.valueOf(width));
			}

			if (height != null) {
				this.module.setHeight(Integer.valueOf(height));
			}

			if (this.moduleChangedListener != null) {
				this.moduleChangedListener.onModuleChanged();
			}
		}
	}

	public void setNewPageDimensions(String height, String width) {
		if (this.module != null) { // Page not selected
			return;
		}

		StringPropertyWidget widthPropertyWidget = (StringPropertyWidget) this.pagePropertiesWidgets.get(DictionaryWrapper.get("width"));
		StringPropertyWidget heightPropertyWidget = (StringPropertyWidget) this.pagePropertiesWidgets.get(DictionaryWrapper.get("height"));

		widthPropertyWidget.setValue(width);
		heightPropertyWidget.setValue(height);
	}

	public void setTextEditor(TextEditorWidget textEditor) {
		this.textEditor = textEditor;
	}
	
	public void setBlocksEditor(BlocksEditorWidget blocksEditor) {
		this.blocksEditor = blocksEditor;
	}

	public void setHTMLEditor(HTMLEditorWidget htmlEditor) {
		this.htmlEditor = htmlEditor;
	}

	public void setItemsEditor(ItemsEditorWidget itemsEditor) {
		this.itemsEditor = itemsEditor;
	}
	
	public void setStaticItemsEditor(StaticItemsEditorWidget staticItems) {
		this.staticItemsEditor = staticItems;
	}

	public void updateElementsTexts() {
		this.title.setInnerText(DictionaryWrapper.get("properties"));
		$(".propertiesPanel").find("span#moduleTypeLabel").text(DictionaryWrapper.get("module_title"));
		this.nodeName.setInnerText((DictionaryWrapper.get("module_title")));
		this.moduleDoc.setAttribute("data-tooltip", DictionaryWrapper.get("documentation"));
	}

	public void setFileSelector(FileSelectorWidget fileSelector) {
		this.fileSelector = fileSelector;
		this.htmlEditor.setFileSelector(fileSelector);
		this.itemsEditor.setFileSelector(fileSelector);
	}

	public void setLayoutEditor(LayoutEditorWidget layout) {
		this.layoutEditor = layout;
	}

	public void setDocViewer(DocViewerWidget docViewer) {
		this.docViewer = docViewer;
	}

	public void adjustToContent(IModuleModel module) {
		if(this.modulePropertiesWidgets.isEmpty()) {
			return;
		}

		if (module.getLayout().hasLeft() && module.getLayout().hasRight() || module.getLayout().hasTop() && module.getLayout().hasBottom()) {
			return;
		}

		StringPropertyWidget heightPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Height");
		StringPropertyWidget widthPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Width");
		StringPropertyWidget topPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Top");
		StringPropertyWidget leftPropertyWidget = (StringPropertyWidget) this.modulePropertiesWidgets.get("Left");

		int givenModuleHeight, givenModuleWidth, givenModuleTop, givenModuleLeft;

		try {
			givenModuleHeight = Integer.parseInt(heightPropertyWidget.getValue().toString());
		} catch(NumberFormatException e) {
			givenModuleHeight = 0;
		}

		try {
			givenModuleWidth = Integer.parseInt(widthPropertyWidget.getValue().toString());
		} catch(NumberFormatException e) {
			givenModuleWidth = 0;
		}

		try {
			givenModuleTop = Integer.parseInt(topPropertyWidget.getValue().toString());
		} catch(NumberFormatException e) {
			givenModuleTop = 0;
		}

		try {
			givenModuleLeft = Integer.parseInt(leftPropertyWidget.getValue().toString());
		} catch(NumberFormatException e) {
			givenModuleLeft = 0;
		}

		// Usual selector $('#<id>') will not work (it will throw exception) if
		// module ID contains spaces.
		GQuery $module = $(".ic_page.ic_main").find("[id='" + module.getId() + "']");

		int moduleRealHeight;
		int moduleRealWidth;

		if($module.css("box-sizing") == "border-box"){
			moduleRealHeight = $module.outerHeight();
			moduleRealWidth = $module.outerWidth();
		}else{
			moduleRealHeight = $module.height();
			moduleRealWidth = $module.width();
		}

		int moduleRealTop = $module.isVisible() ? $module.position().top : module.getTop();
		int moduleRealLeft = $module.isVisible() ? $module.position().left : module.getLeft();

		if (moduleRealHeight != givenModuleHeight || moduleRealWidth != givenModuleWidth ||
				moduleRealTop != givenModuleTop || moduleRealLeft != givenModuleLeft) {

			int roundedModuleRealHeight = Math.round(moduleRealHeight);
			int roundedModuleRealWidth = Math.round(moduleRealWidth);
			int roundedModuleRealLeft = Math.round(moduleRealLeft);
			int roundedModuleRealTop = Math.round(moduleRealTop);

			this.setNewDimensions(Integer.toString(roundedModuleRealHeight), Integer.toString(roundedModuleRealWidth), true);
			this.setNewPosition(Integer.toString(roundedModuleRealLeft), Integer.toString(roundedModuleRealTop), null, null, true);
		}
	}

	public void setChapter(IChapter chapter) {
		this.removeLayoutListener();

		this.module = null;
		this.nodeName.setInnerText(chapter.getName());

		this.clearPropertiesListView();

		this.addChapterProperties(chapter);
	}

	private void addChapterProperties(final IChapter chapter) {
		IPropertyProvider propertyProvider = (IPropertyProvider) chapter;
		int propertyCount = propertyProvider.getPropertyCount();

		for (int i = 0; i < propertyCount; i++) {
			final IProperty property = propertyProvider.getProperty(i);
			String propertyName = this.getPropertyName(property);

			StringPropertyWidget propertyWidget = new StringPropertyBuilder(propertyName, property.getValue()).
				listener(new StringPropertyChangeListener() {
					@Override
					public void onChange(String value) {
						property.setValue(value);
						PropertiesWidget.this.nodeName.setInnerText(chapter.getName());
						PropertiesWidget.this.onChapterEdit.execute();
					}
				}).build();
			this.propertiesList.add(propertyWidget);
		}

		MainPageUtils.updateWidgetScrollbars("properties");
	}

	private String getPropertyName(IProperty property) {
		String propertyName = property.getDisplayName();

		if (propertyName.equals("")) {
			propertyName = property.getName();
		}
		return propertyName;
	}

	public void clear() {
		this.removeLayoutListener();

		this.module = null;
		this.nodeName.setInnerText("");

		this.clearPropertiesListView();
	}

	public void setModuleChangedListener(ModuleChangedListener listener) {
		this.moduleChangedListener = listener;
	}
	
	public Map<String, Composite> getModuleProperties() {
		return this.modulePropertiesWidgets;
	}
	
	
 	private void clearPropertiesListView() {
		Iterator<Widget> it = this.propertiesList.iterator();
		int lastItemCount = this.propertiesList.getWidgetCount();
		//If it.remove() can't remove element then break loop. That loop may be infinite without that
	    while (it.hasNext()) {
	        it.next();
	        it.remove();
	        if (this.propertiesList.getWidgetCount() == lastItemCount){
	        	break;
	        } else {
	        	lastItemCount = this.propertiesList.getWidgetCount();
	        }
	      }
	}
 	
	private void showModuleDoc () {
		$("#moduleDoc").show();
	}

	private void hideModuleDoc () {
		$("#moduleDoc").hide();
	}
	
	private void removeLayoutListener() {
		if (this.module != null) {
			this.module.removePropertyListener(this.layoutPropertyListener);
		}
	}

	private void addHeadersFootersList(){
		String selectedHeader = this.currentPage.getHeaderId();
		String selectedFooter = this.currentPage.getFooterId();

		this.createHeaderOptions();
		this.createFooterOptions();

		this.showHeadersOptions(selectedHeader);
		this.showFootersOptions(selectedFooter);
	}

    private void createHeaderOptions() {
 		this.headerOptions = new LinkedHashMap<String, String>();
 		
 		this.headerOptions.put("", DictionaryWrapper.get("Header_default"));
 		this.headerOptions.put("None", DictionaryWrapper.get("Header_none"));
 		
		ArrayList<Page> headers = this.content.getHeaders();

		for (Page header : headers) {
			this.headerOptions.put(header.getId(), header.getName());
		}
 	}

	private void showHeadersOptions(String selectedHeader) {
		String[] headerKeys = this.getHeaderKeys();
		String[] headerTexts = this.getHeaderValues();
		
		if (!this.currentPage.hasHeader()) {
			selectedHeader = "None";
		}

		Widget headerWidget = new SelectPropertyBuilder(DictionaryWrapper.get("Header"), headerKeys)
		.listener(new SelectPropertyChangeListener() {
			@Override
			public void onChange(String value) {
				if (value.equals("None")) {
					currentPage.setHasHeader(false);
				} else {
					currentPage.setHasHeader(true);
					currentPage.setHeaderId(value);
				}
				onPageEdit.execute();
				onSave.execute();
			}
		}).selected(selectedHeader).optionTexts(headerTexts).build();
		
		if (headerWidget != null) {
			this.propertiesList.add(headerWidget);
		}
	}
 	
 	private String[] getHeaderKeys() {
 		int size = headerOptions.keySet().size();
 		String[] keys = new String[size];
 		return this.headerOptions.keySet().toArray(keys);
 	}
 	
 	private String[] getHeaderValues() {
 		int size = this.headerOptions.values().size();
 		String[] values = new String[size]; 
 		return this.headerOptions.values().toArray(values);
 	}
 	
 	private void createFooterOptions() {
 		this.footerOptions = new LinkedHashMap<String, String>();
 	
 		this.footerOptions.put("", DictionaryWrapper.get("Footer_default"));	
		this.footerOptions.put("None",  DictionaryWrapper.get("Footer_none"));
		
		ArrayList<Page> footers = this.content.getFooters();
		
		for (Page footer : footers) {
			this.footerOptions.put(footer.getId(), footer.getName());
		}
 	}

 	private void showFootersOptions(String selectedFooter) {
		String[] footerKeys = this.getFooterKeys();
		String[] footerTexts = this.getFooterValues();
		
		if (!this.currentPage.hasFooter()) {
			selectedFooter = "None";
		} 
		
		Widget footerWidget = new SelectPropertyBuilder(DictionaryWrapper.get("Footer"), footerKeys)
		.listener(new SelectPropertyChangeListener() {
			@Override
			public void onChange(String value) {
				if (value.equals("None")) {
					currentPage.setHasFooter(false);
				} else {
					currentPage.setHasFooter(true);
					currentPage.setFooterId(value);
				}
				onPageEdit.execute();
				onSave.execute();
			}
		})
		.selected(selectedFooter).optionTexts(footerTexts).build();
		
		if (footerWidget != null) {
			this.propertiesList.add(footerWidget);
		}
	}
 	
 	private String[] getFooterKeys() {
 		int size = this.footerOptions.keySet().size();
 		String[] keys = new String[size];
 		return this.footerOptions.keySet().toArray(keys);
 	}
 	
 	private String[] getFooterValues() {
 		int size = this.footerOptions.values().size();
 		String[] values = new String[size]; 
 		return this.footerOptions.values().toArray(values);
 	}
 	
}
