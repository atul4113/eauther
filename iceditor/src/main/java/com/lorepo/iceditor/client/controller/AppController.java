package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.TreeMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Window;
import com.google.gwt.xml.client.Document;
import com.google.gwt.xml.client.XMLParser;
import com.lorepo.iceditor.client.EditorConfig;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.actions.api.ISelectionController;
import com.lorepo.iceditor.client.actions.api.IServerService.IRequestListener;
import com.lorepo.iceditor.client.controller.addons.AddonListLoader;
import com.lorepo.iceditor.client.controller.addons.UpdatePageAddons;
import com.lorepo.iceditor.client.template.UpdateTemplateTask;
import com.lorepo.iceditor.client.ui.AppFrame;
import com.lorepo.iceditor.client.ui.dlg.ModuleInfo;
import com.lorepo.iceditor.client.ui.widgets.modals.SingleButtonModalListener;
import com.lorepo.iceditor.client.ui.widgets.modals.QuestionModalListener;
import com.lorepo.iceditor.client.ui.widgets.modules.add.ModulesInfoUtils;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.properties.ModuleChangedListener;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;
import com.lorepo.icf.properties.IProperty;
import com.lorepo.icf.properties.IPropertyListener;
import com.lorepo.icf.utils.ILoadListener;
import com.lorepo.icf.utils.JavaScriptUtils;
import com.lorepo.icf.utils.URLUtils;
import com.lorepo.icf.utils.dom.DOMInjector;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.ContentDataLoader;
import com.lorepo.icplayer.client.framework.module.IStyleListener;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.IModuleListListener;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.addon.AddonDescriptorFactory;
import com.lorepo.icplayer.client.model.addon.AddonEntry;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.xml.IProducingLoadingListener;
import com.lorepo.icplayer.client.xml.IXMLFactory;
import com.lorepo.icplayer.client.xml.content.ContentFactory;
import com.lorepo.icplayer.client.xml.page.PageFactory;

public class AppController implements IAppController{

	private	Content	contentModel;
	private ContentModyficationController modyficationController;
	private	ThemeController	themeController;
	private AppFrame appFrame;
	private ActionFactory actionFactory;
	private Page currentPage;
	private IActionService actionServices;
	private SelectionController selectionController;
	
	private ContainerUrl urls;
	
	private EditorConfig config;
	private MediaProviderImpl imageProvider;
	private final HashMap<String, AddonEntry> addonEntries = new HashMap<String, AddonEntry>();
	private ModulesInfoUtils modulesInfoUtils;
	private UndoManager undoManager;
	private boolean isEditoeInitialized = false;
	private HashMap<String, ModuleInfo> favouriteModules = new HashMap<String, ModuleInfo>();
	
	private AbstractAction onRefreshSemiResponsiveEditingWidgets;
	private boolean isShowingResourceLoadingError = false;
	private boolean isFirstPageLoaded = false;

	private static boolean isAllowClose = true;
	private boolean isSavingStyles = false;
	
	private final IPropertyListener pagePropertyListener = new IPropertyListener() {
		@Override
		public void onPropertyChanged(IProperty property) {
			getUndoManager().add(currentPage.toXML());
			saveCurrentPageAndContent();
		}
	};

	protected AppController() {
		// Only for tests purposes!!!
	}
	
	public AppController(AppFrame view, EditorConfig config){
		this.appFrame = view;
		this.config = config;
		modyficationController = new ContentModyficationController(this);
		
		urls = new ContainerUrl(); 
		
		initSelectionController();
		actionServices = new ActionServices(this);
		themeController = new ThemeController(this);
		actionFactory = new ActionFactory(this);
		modyficationController.setActionService(actionServices);

		prepareModulesInfos();
		connectActionFactory();
		loadAddonList();
		setAppFrames();
		
		onRefreshSemiResponsiveEditingWidgets = actionFactory.getAction(ActionType.refreshSemiResponsiveLayoutEditingWidgets);
	}
	
	public boolean isAllowClose() {
		return isAllowClose; 
	}
	
	public void setIsAllowClose(boolean isClose) {
		isAllowClose = isClose; 
	}
	
	@Override
	public int getCommonPageIndex(String pageId) {
		return contentModel.getCommonPageIndex(pageId);
	}

	private void initSelectionController() {
		selectionController = new SelectionController(this);
		selectionController.initJavaScriptAPI();
		selectionController.setContentWrapper(appFrame.getContentWrapper());
		selectionController.setPresentationWidget(appFrame.getPresentation());

		appFrame.getModules().setSelectionController(selectionController);
		appFrame.getPages().setSelectionController(selectionController);
	}

	private void prepareModulesInfos() {
		this.modulesInfoUtils = new ModulesInfoUtils(actionFactory, this);

		appFrame.getAddModule().setModulesInfoUtils(this.modulesInfoUtils);
		appFrame.getMenu().setModulesInfoUtils(this.modulesInfoUtils);
		appFrame.getFavouriteModules().setModulesInfoUtils(this.modulesInfoUtils);
	}

	private void connectActionFactory() {
		selectionController.setActionFactory(actionFactory);

		this.appFrame.getWorkspace().setActionFactory(actionFactory);

		this.appFrame.getPages().setActionFactory(actionFactory);
		this.appFrame.getHeaderMenu().setActionFactory(actionFactory);
		this.appFrame.getMenu().setActionFactory(actionFactory);
		this.appFrame.getPresentation().setActionFactory(actionFactory);

		this.appFrame.getItemsEditor().setActionFactory(actionFactory);
		this.appFrame.getStaticItemsEditor().setActionFactory(actionFactory);
		this.appFrame.getLayoutEditor().setActionFactory(actionFactory);

		this.appFrame.getProperties().setActionFactory(actionFactory);
		this.appFrame.getModules().setActionFactory(actionFactory);
		this.appFrame.getStyles().setActionFactory(actionFactory);
		this.appFrame.getAddWCAG().setActionFactory(actionFactory);
		this.appFrame.getAddWCAG().setAppController(this);
		
		this.appFrame.getEditCSS().setActionFactory(actionFactory);
		this.appFrame.getEditSemiResponsiveLayouts().setActionFactory(actionFactory);
	}

	private void loadAddonList() {
		final AddonListLoader loader = new AddonListLoader(config.apiURL);
		loader.load(new ILoadListener() {
			@Override
			public void onFinishedLoading(Object obj) {
				List<AddonEntry> entries = new ArrayList<AddonEntry>();

				for(AddonEntry entry : loader.getEntries()){
					addonEntries.put(entry.getId(), entry);

					if (!config.excludeAddons.contains(entry.getId())) {
						entries.add(entry);
					}
				}

				appFrame.getMenu().setPrivateAddons(entries);
			}

			@Override
			public void onError(String reason) {
				error("Load addon list", reason);
			}
		});
	}

	private void setAppFrames() {
		appFrame.getProperties().setAppFrame(appFrame);
	}
	
	private void setContents() {
		this.appFrame.getPages().setModel(this.contentModel);
		this.appFrame.getProperties().setContent(this.contentModel);
		this.appFrame.getPresentation().setContent(this.contentModel);
	}

	@Override
	public Page getCurrentPage() {
		return this.currentPage;
	}

	@Override
	public ContentModyficationController getModyficationController() {
		return modyficationController;
	}

	@Override
	public AppFrame getAppFrame() {
		return appFrame;
	}

	public Content getModel() {

		return contentModel;
	}

	public ThemeController getTheme(){
		return themeController;
	}


	public void loadContent(String url){
		setContent(url); 
		createContentFactory(); 
	}
	
	public void createContentFactory() {
		IXMLFactory contentFactory = ContentFactory.getInstanceWithAllPages();
		contentFactory.load(getContentUrl(), new IProducingLoadingListener() {
			public void onFinishedLoading(Object content) {
				contentModel = (Content) content;
				setContents();
//				contentModel.connectHandlers();
				onContentLoaded();
			}

			public void onError(String error) {
				showLoadingErrorMessage("content", error);
			}
		});
	}
	
	public void setContent(String url) {
		urls.setContentURL(url); 
	}

	@Override
	public String getContentUrl() {
		return urls.getContentURL();
	}

	protected void onContentLoaded() {
	    imageProvider = new MediaProviderImpl(contentModel, this);
	    appFrame.setImageProvider(imageProvider);

		loadContentInitialStyles();

		ContentDataLoader loader = new ContentDataLoader(contentModel.getBaseUrl());
		loader.setDefaultLayoutID(contentModel.getActualSemiResponsiveLayoutID());
		loader.addAddons(contentModel.getAddonDescriptors().values());

		for (Page header : this.contentModel.getHeaders()) {
			loader.addPage(header);
		}
		for (Page footer : this.contentModel.getFooters()) {
			loader.addPage(footer);
		}

		loader.load(new ILoadListener() {
			@Override
			public void onFinishedLoading(Object obj) {
				switchToPage(contentModel.getPages().getAllPages().get(0), false);
			}

			@Override
			public void onError(String reason) {
				showLoadingErrorMessage("commons", reason);
			}
		});

	}

	private void loadContentInitialStyles() {
		DOMInjector.appendStyle(contentModel.getActualStyle());
		loadTheme();
		updateCss(contentModel.getActualStyle());
	}


	private void loadTheme() {
		if(contentModel.getMetadataValue("theme.href") != null){
			themeController.loadTheme(contentModel.getMetadataValue("theme.href"),
					new ILoadListener() {
						@Override
						public void onFinishedLoading(Object obj) {}
						@Override
						public void onError(String reason) {
							error("loadTheme", reason);
						}
			});
		}
	}

	@Override
	public void saveContent(){

		IRequestListener ireql = new IRequestListener() {

			@Override
			public void onFinished(String responseText) {
				if (isSavingStyles) {
					isSavingStyles = false;
					appFrame.getNotifications().addMessage(DictionaryWrapper.get("saved_css"), NotificationType.success, false);
				} else {
					appFrame.getNotifications().addMessage(DictionaryWrapper.get("content_saved"), NotificationType.success, false);
				}
			}

			@Override
			public void onError(int server_error) {
				if (isSavingStyles) {
					isSavingStyles = false;
				}
				serverErrorMessage(server_error, "cant_save_content");
			}
		};

		saveContent(ireql);
		getModyficationController().setContentAsModified(false);
	}

	@Override
	public void saveContent(IRequestListener callback) {
		String contents = contentModel.toXML();

		actionServices.getServerService().saveFile(urls.getContentURL(), contents, callback);
	}

	@Override
	public void savePage(final IRequestListener parentCallback) {
	    savePage(currentPage, parentCallback);
	}
	public void savePage(Page page, final IRequestListener parentCallback) {
		if (page == null) {
			return;
		}
		final Page pageBeforeSave = page;
		IRequestListener saveFileCallback = new IRequestListener() {
			@Override
			public void onFinished(String responseText) {
				getModyficationController().setModified(false, pageBeforeSave.getId());
				getModyficationController().checkAllPagesSaved();
				parentCallback.onFinished(responseText);
			}

			@Override
			public void onError(int server_error) {
				parentCallback.onError(server_error);
			}
		};
		
		page.setGroupedModules(selectionController.getPageGroupsCopy(page.getId()));
		actionServices.getServerService().saveFile(page.getURL(), page.toXML(), saveFileCallback);
	}

	@Override
	public void saveCurrentPageAndContent() {
		IRequestListener callback = new IRequestListener() {
			private int errorCount=0;
			private int finishedCount=0;
			private int reason_code;

			private void updateLogic() {
				if (finishedCount + errorCount == 2) {
					if (finishedCount == 2) {
						appFrame.getNotifications().addMessage(DictionaryWrapper.get("page_saved"), NotificationType.success, false);
					} else {
						serverErrorMessage(reason_code, "cant_save_page");
					}
				}
			}

			@Override
			public void onFinished(String responseText) {
				finishedCount++;
				updateLogic();
			}

			@Override
			public void onError(int reason_code) {
				this.reason_code = reason_code;
				errorCount++;
				updateLogic();
			}
		};

		getCurrentPage().setModulesMaxScore(getAppFrame().getPresentation().getPageMaxScore());
		saveContent(callback);
		savePage(callback);
	}

	@Override
	public void refreshStyles(String style){
		this.refreshStylesOnly(style);
		appFrame.getPresentation().refreshView();
	}
	

	public void refreshStylesOnly(String style) {
		updateCss(style);
		DOMInjector.appendStyle(style);
	}
	
	@Override
	public void switchToPage(final Page page, final ILoadListener listener, final boolean isPageSelect){
		if(page == currentPage){
			return;
		}

		_switchPage(page, listener, isPageSelect);
	}

	private void _switchPage(final Page page, final ILoadListener listener, final boolean isPageSelect) {
		final Page lastPage = this.currentPage;
		closeCurrentPage(false);

		if(!page.isLoaded()){
			if (!appFrame.isLoadingPresentationVisible()) {
				appFrame.showLoadingPage();
			}

			// Load new page
			String baseUrl = this.contentModel.getBaseUrl();

			String url = URLUtils.resolveURL(baseUrl, page.getHref());

			PageFactory factory = new PageFactory((Page) page);
			factory.load(url, new IProducingLoadingListener() {
				@Override
				public void onFinishedLoading(Object producedItem) {
					Page page = (Page) producedItem;
					updateAddons(page);

					if (!isPageSelect) {
						appFrame.getPages().refresh();
					}

					setCurrentPage(page);

					appFrame.hideLoadingPage();
					appFrame.hideLoadingPresentation();

					if(listener != null){
						listener.onFinishedLoading(page);
					}

					selectionController.setGroupedModulesFromXML(page);
					executeEditorInitializedFunction();
					initEditorOptions();
					
					isFirstPageLoaded = true;
				}

				@Override
				public void onError(String error) {
					if (lastPage != null) {
						setCurrentPage(lastPage);
						initEditorOptions();
						appFrame.hideLoadingPage();
						appFrame.hideLoadingPresentation();
					} 
					showLoadingErrorMessage("page", error);
				}
			});
		} else {
			appFrame.showLoadingPage();
			setCurrentPage(page);
			initEditorOptions();
			appFrame.hideLoadingPage();
		}
	}

	private void executeEditorInitializedFunction() {
		if(!isEditoeInitialized){
			iceOnEditorInitialized();
			isEditoeInitialized = true;
		}
	}

	@Override
	public void initEditorOptions() {
		this.appFrame.getMenu().setGridOptions(getActionServices().getModel());
		this.appFrame.getMenu().setRulersOptions(getActionServices().getModel());
		this.appFrame.getPresentation().setRulers(getActionServices().getModel(), currentPage.getRulers());
	}
	
	public void updateFavouriteModules() {
		modulesInfoUtils.setModules(DictionaryWrapper.get("favourite_menu"), getFavouriteModules());
		
		appFrame.getMenu().updateFavouriteModulesMenu(getFavouriteModules());
		appFrame.getAddModule().updateFavouriteModulesMenu(getFavouriteModules());
	}

	public static native void iceOnEditorInitialized() /*-{
	  $wnd.iceOnEditorInitialized();
	}-*/;

	@Override
	public void switchToChapter(IChapter chapter) {
		closeCurrentPage(true);

		selectionController.setContentNode(chapter);
		appFrame.getPresentation().setChapter(chapter);
		appFrame.getProperties().setChapter(chapter);
	}

	public void closeCurrentPage(boolean hideCommons) {
		if (currentPage == null) {
			return;
		}

		undoManager = null;

		if (getModyficationController().isContentModified()) {
			saveContent();
		}

		getModyficationController().savePageIfModified(null);

		currentPage.removePropertyListener(pagePropertyListener);
		currentPage = null;

		appFrame.getPresentation().removeAllModules();
		appFrame.getModules().clear();

		selectionController.clearSelectedModules();
		selectionController.setContentNode(null);

		if (hideCommons) {
			appFrame.getPresentation().showHeader(false);
			appFrame.getPresentation().showFooter(false);
		}
	}


	private void updateAddons(Page page){
		UpdatePageAddons addonUpdater = new UpdatePageAddons(contentModel.getAddonDescriptors());
		addonUpdater.update(page);
	}


	private void setCurrentPage(Page page) {
		currentPage = page;
		selectionController.setContentNode(page);
		currentPage.addPropertyListener(pagePropertyListener);
		undoManager = createUndoManagerForPage(page);

		IChapter chapter = contentModel.getParentChapter(currentPage);
		if (chapter == contentModel.getCommonPages()) {
			setHiddenHeaderAndFooter();
			appFrame.getPresentation().setPage(page);
		} else {
			appFrame.getPresentation().setPage(page);
			this.setHeaderAndFooter();
		}

		setCurrentPageModyficationFlag();
		connectPageHandlers();
		appFrame.getPages().setSelectedNode(page);
		appFrame.getProperties().setPage(page);
		appFrame.getModules().setPage(page);
		appFrame.getStyles().setPage(page);
	}

	private UndoManager createUndoManagerForPage(Page page) {
		return new UndoManager(page, new IUndoManager.UndoManagerEventListener() {
			@Override
			public void onPageXMLChanged(String xml) {
				Document dom = XMLParser.parse(xml);
				currentPage.reload(dom.getDocumentElement());

				appFrame.getModules().setPage(currentPage);
				appFrame.getProperties().setPage(currentPage);
				appFrame.getPages().refreshSelectedNode();
				List<IModuleModel> selectedModulesOld = selectionController.getSelectedModulesList();
				List<IModuleModel> selectedModules = new ArrayList<IModuleModel>(selectedModulesOld);
				selectionController.clearSelectedModules();
				
				selectionController.setGroupedModulesFromXML(currentPage);
				
				for (IModuleModel module : currentPage.getModules()) {
					for (IModuleModel selectedModule : selectedModules) {
						if(selectedModule.getId().equals(module.getId())){
							selectionController.addModule(module);
						}
					}
				}

				appFrame.getPresentation().setPage(currentPage);
				appFrame.getStyles().setPage(currentPage);
			}
		});
	}

	private void setCurrentPageModyficationFlag() {
		boolean modificationFlag = getModyficationController().isPageModified(currentPage.getId());
		getModyficationController().setModified(modificationFlag);
	}

	private void connectPageHandlers() {
		currentPage.getModules().addListener(new IModuleListListener() {
			@Override
			public void onModuleRemoved(IModuleModel module) {
				getModyficationController().setModified(true);
			}

			@Override
			public void onModuleChanged(IModuleModel module) {
				getModyficationController().setModified(true);
			}

			@Override
			public void onModuleAdded(IModuleModel module) {
				getModyficationController().setModified(true);
			}
		});

		IPropertyListener groupPropertyListener = new IPropertyListener() {
			@Override
			public void onPropertyChanged(IProperty source) {
				getModyficationController().setModified(true);
			}
		};

		for (Group group : currentPage.getGroupedModules()) {
			group.addPropertyListener(groupPropertyListener);
		}

		currentPage.addStyleListener(new IStyleListener() {
			@Override
			public void onStyleChanged() {
				getModyficationController().setModified(true);
			}
		});

		ModuleChangedListener moduleChangedListener = new ModuleChangedListener() {
			@Override
			public void onModuleChanged() {
				if(!isAddToDrag()){
					getUndoManager().add(currentPage.toXML());
				}
			}
		};

		appFrame.getProperties().setModuleChangedListener(moduleChangedListener);
		appFrame.getItemsEditor().setModuleChangedListener(moduleChangedListener);
		appFrame.getStaticItemsEditor().setModuleChangedListener(moduleChangedListener);
		
		appFrame.getItemsEditor().setModals(appFrame.getModals());
		appFrame.getStaticItemsEditor().setModals(appFrame.getModals());
		appFrame.getHTMLEditor().setModals(appFrame.getModals());
		appFrame.getTextEditor().setModals(appFrame.getModals());
		appFrame.getBlocksEditor().setModals(appFrame.getModals());

		MainPageUtils.appFrame = appFrame;
	}
	
	public static native boolean isAddToDrag() /*-{
	  return $wnd.isAddToDragAction();
	}-*/;

	private void setHiddenHeaderAndFooter() {
		appFrame.getPresentation().showHeader(false);
		appFrame.getPresentation().showFooter(false);
	}
	
	private void setHeaderAndFooter() {
		this.setHeader();
		this.setFooter();
	}


	private void updateCss(String css) {
		appFrame.getStyles().setCSS(css);
	}


	@Override
	public void setThemeURL(String themeURL, final ILoadListener loadListener) {

		contentModel.setMetadataValue("theme.href", themeURL);
		themeController.loadTheme(themeURL, new ILoadListener() {

			@Override
			public void onFinishedLoading(Object obj) {
				onThemeChanged(themeController.getTheme());
				onRefreshSemiResponsiveEditingWidgets.execute();
				loadListener.onFinishedLoading(obj);
			}

			@Override
			public void onError(String error) {
				loadListener.onError(error);
			}
		});
	}

	public IActionService getActionServices() {
		return actionServices;
	}

	@Override
	public IUndoManager getUndoManager() {
		return undoManager;
	}

	@Override
	public void close() {
		isAllowClose = false;
		Window.Location.replace(getNextURL());
	}

	@Override
	public int getCurrentPageIndex() {
		Page currentPage = actionServices.getAppController().getCurrentPage();
		int pageCount = actionServices.getModel().getPageCount();

		for (int i = 0; i < pageCount; i++) {
			if (actionServices.getModel().getPage(i).getId().compareTo(currentPage.getId()) == 0) {
				return i;
			}
		}

		return 0;
	}

	@Override
	public void previewInNewTab() {
		Page page = getCurrentPage();

		int commonPageIndex = getCommonPageIndex(page.getId());
		int currentPageIndex = getCurrentPageIndex();
		String tabURL = getPreviewUrlInNewTab();

		if (commonPageIndex >= 0) {
			tabURL += "#commons_" + (commonPageIndex + 1);
		} else if (currentPageIndex > 0) {
			tabURL += "#" + (currentPageIndex + 1);
		}

		Window.open(tabURL, "_blank", null);
	}

	@Override
	public void abandon() {
		appFrame.getModals().addModal(DictionaryWrapper.get("confirm_abandon_all_changes"), new QuestionModalListener() {
			@Override
			public void onDecline() {
				isAllowClose = true; 
			}

			@Override
			public void onAccept() {
				isAllowClose = false; 
				Window.Location.replace(getAbandonUrl());
			}
		});
	}

	

	@Override
	public void addAddon(AddonDescriptor descriptor) {

		if(!contentModel.getAddonDescriptors().containsKey(descriptor.getAddonId())){
			contentModel.getAddonDescriptors().put(descriptor.getAddonId(), descriptor);
			DOMInjector.injectJavaScript(descriptor.getCode());
			String css = descriptor.getCSS().replace("url(\'resources/",
					"url(\'" + GWT.getModuleBaseForStaticFiles() + "addons/resources/");
			DOMInjector.injectStyleAtStart(css);
		}
	}

	@Override
	public ISelectionController getSelectionController() {
		return selectionController;
	}


	public void setNextURL(String url) {
		urls.setNextURL(url); 
	}

	public String getNextURL() {
		return urls.getNextURL(); 
	}

	
	public void setPreviewUrlInNewTab(String url) {
		urls.setPreviewURLInNewTab(url);
	}

	public void setPreviewUrl(String url) {
		urls.setPreviewUrl(url); 
	}
	
	
	@Override
	public String getPreviewUrlInNewTab() {
		return urls.getPreviewURLInNewTab();
	}
	
	@Override
	public String getPreviewUrl() {
		return urls.getPreviewUrl();
	}

	public void setContainerUrl(ContainerUrl urls) {
		this.urls = urls; 
	}
	
	public void setAbandonUrl(String url) {
		urls.setAbandonUrl(url); 
	}
	
	public String getAbandonUrl() {
		return urls.getAbandonUrl(); 
	}

	@Override
	public String getAddonURL(String addonId) {
		AddonEntry localEntry = AddonDescriptorFactory.getInstance().getEntry(addonId);
		if(localEntry != null){
			return localEntry.getDescriptorURL();
		}else if(addonEntries.containsKey(addonId)){
			return addonEntries.get(addonId).getDescriptorURL();
		}
		return "";
	}

	@Override
	public ActionFactory getActionFactory() {
		return actionFactory;
	}

	@Override
	public Collection<AddonEntry> getAddonList() {
		return AddonDescriptorFactory.getInstance().getEntries();
	}

	@Override
	public void switchToPage(Page page, boolean isPageSelect) {
		switchToPage(page, null, isPageSelect);
	}

	@Override
	public void switchPageSemiResponsiveLayout(Page page, boolean isPageSelected) {
		this._switchPage(page, null, isPageSelected);
	}
	
	private void onThemeChanged(Content themeContent) {
		if(themeContent != null){
			new UpdateTemplateTask().execute(themeContent, this.contentModel);
			this.refreshStyles(this.contentModel.getActualStyle());

		}
	}
	
	private void error(String where, String reason) {
		JavaScriptUtils.alert(where + " > " + reason);
	}

	@Override
	public void serverErrorMessage(int status_code, String unsuccessful_action_label) {
		String error_label = "";
		switch (status_code) {
		case 403:
			error_label = "error_forbidden";
			break;
		case 404:
			error_label = "error_not_found";
			break;
		case 500:
			error_label = "error_server_error";
			break;
		case 999:
		default:
			error_label = "error_unknown_error";
			break;
		}

		String reason_string = DictionaryWrapper.get(error_label);
		JavaScriptUtils.alert(DictionaryWrapper.get(unsuccessful_action_label) + reason_string);
	}
	
	public void showLoadingErrorMessage(String type, String reason ) {
	    if (isShowingResourceLoadingError) 
	        return;
	        
		if (!isFirstPageLoaded && !type.equals("theme")) {	
			isShowingResourceLoadingError = true;
			JavaScriptUtils.log(reason + "Can't load " + type + ". Click OK to be moved to the previous view.");
			
            appFrame.getModals().addModalSingleButton("Can't load " + type + ". Click OK to be moved to the previous view.", new SingleButtonModalListener() {

                public void onAccept() {
                	Window.Location.replace(getNextURL());	
                	isShowingResourceLoadingError = false;
                }
            });  
		}
		else {
			String message = "";
			if (type.equals("theme")) {
				message =  DictionaryWrapper.get("Editor_load_theme_error");
			} else {
				message = "Error loading " + type + ". Please try again.";
			}
			JavaScriptUtils.log("reason" + message);
			
			appFrame.getModals().addModalSingleButton(message, new SingleButtonModalListener() {
				
				public void onAccept() {
					isShowingResourceLoadingError = false;
				}
			});
		}	
	}

	public HashMap<String, ModuleInfo> getFavouriteModules() {
		return favouriteModules;
	}

	public void setFavouriteModules(HashMap<String, ModuleInfo> favourities) {
		TreeMap<String, String> orderedNames = new TreeMap<String, String>();
		HashMap<String, ModuleInfo> orderedModules = new HashMap<String, ModuleInfo>();
		
		for (String key : favourities.keySet()) {
			orderedNames.put(favourities.get(key).name, key);
		}
		
		for (String name : orderedNames.values()) {
			orderedModules.put(name, favourities.get(name));
		}
		
		this.favouriteModules = orderedModules;
	}

	public void prepareAndSetFavouriteModules(List<String> favouriteModules) {
		HashMap<String, ModuleInfo> favourities = new HashMap<String, ModuleInfo>();
		HashMap<String, ModuleInfo> addonsAndModules = modulesInfoUtils.getAddonsAndModules();
		
		for (String module : favouriteModules) {
			favourities.put(module, addonsAndModules.get(module));
		}
		
		setFavouriteModules(favourities);
		modulesInfoUtils.addFavouritiesModules();
		appFrame.getMenu().updateFavouriteModulesMenu(getFavouriteModules());
		appFrame.getAddModule().updateFavouriteModulesMenu(getFavouriteModules());

		appFrame.getFavouriteModules().setFavouriteModules(getFavouriteModules());
	}
	
	public void saveFavouriteModulesURL(String url) {
		urls.setFavouriteModulesURL(url); 
	}
	
	public String getFavouriteModulesURL() {
		return urls.getFavouriteModulesURL();
	}
	
	public void setRenderURL(String url) {
		appFrame.getHTMLEditor().setURLToSave(url);
		appFrame.getItemsEditor().setURLToSave(url);
		appFrame.getStaticItemsEditor().setURLToSave(url);
	}

	private void setHeader() {
		Page header = null;

		if (this.currentPage.hasHeader()){
			header = contentModel.getHeader(this.currentPage);
		}

		if (header != null) {
			appFrame.getPresentation().setHeader(header);
		}
	}

	private void setFooter() {
		Page footer = null;

		if (this.currentPage.hasFooter()) {
			footer = contentModel.getFooter(this.currentPage);
		}

		if (footer != null) {
			appFrame.getPresentation().setFooter(footer);
		}
	}

	@Override
	public boolean isSavingStyles() {
		return isSavingStyles;
	}

	@Override
	public void setIsSavingStyles(boolean isSavingStyles) {
		this.isSavingStyles = isSavingStyles;
	}
}
