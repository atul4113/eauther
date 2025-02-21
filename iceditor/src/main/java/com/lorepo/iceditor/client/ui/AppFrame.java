package com.lorepo.iceditor.client.ui;

import com.google.gwt.user.client.ui.LayoutPanel;
import com.google.gwt.user.client.ui.RootLayoutPanel;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.SimplePanel;
import com.lorepo.iceditor.client.EditorConfig;
import com.lorepo.iceditor.client.actions.api.IAppView;
import com.lorepo.iceditor.client.controller.IMediaProvider;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsWidget;
import com.lorepo.iceditor.client.ui.widgets.HeaderMenuWidget;
import com.lorepo.iceditor.client.ui.widgets.HeaderWidget;
import com.lorepo.iceditor.client.ui.widgets.MenuWidget;
import com.lorepo.iceditor.client.ui.widgets.StylesWidget;
import com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget;
import com.lorepo.iceditor.client.ui.widgets.content.AddWCAGWidget;
import com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget;
import com.lorepo.iceditor.client.ui.widgets.content.FavouriteModulesListWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationLoadingWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PreviewWidget;
import com.lorepo.iceditor.client.ui.widgets.content.SettingsWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.add.AddModulePageWidget;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.iceditor.client.ui.widgets.pages.PagesWidget;
import com.lorepo.iceditor.client.ui.widgets.pages.select.SelectPageWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.HTMLEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.ItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.LayoutEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.StaticItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.TextEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.templates.SelectTemplateWidget;
import com.lorepo.icf.widgets.MessagePopup;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class AppFrame extends LayoutPanel implements IAppView{

	private WorkspaceWidget workspace;
	private boolean cssEditorIsOpen = false;
	public AppFrame(EditorConfig config) {
		this.createUI(config);
	}

	private void createUI(EditorConfig config) {
		this.workspace = new WorkspaceWidget();
		this.workspace.setEditorConfig(config);

		RootLayoutPanel.get().clear();
		RootPanel.get().add(this.workspace);

		this.showLoadingPresentation();
	}

	public void showLoadingPresentation(){
		this.workspace.getPresentationLoading().show();
	}
	
	public void hideLoadingPresentation(){
		this.workspace.getPresentationLoading();
		PresentationLoadingWidget.hide();
	}
	
	public void showLoadingPage(){
		this.workspace.getPageLoading().show();
	}
	
	public void hideLoadingPage(){
		this.workspace.getPageLoading().hide();
	}
	
	public boolean isLoadingPresentationVisible() {
		return this.workspace.getPresentationLoading().isLoadingPresentationVisible();
	}
	
	public void setImageProvider(IMediaProvider mediaProvider){
		this.workspace.getFileSelector().setMediaProvider(mediaProvider);
	}

	
	public void showMessage(String text) {
		MessagePopup popup = new MessagePopup(text);
		int left = (this.getOffsetWidth()-popup.getOffsetWidth())/2;
		popup.setPopupPosition(left, 0);
		popup.show();
	}


	@Override
	public int getPageScrollTopPosition() {
		return this.getPresentation().getPageScrollTopPosition();
	}
	
	public WorkspaceWidget getWorkspace() {
		return this.workspace;
	}

	public HeaderWidget getHeader() {
		return this.workspace.getHeader();
	}
	
	public SimplePanel getContentWrapper() {
		return this.workspace.getContentWrapper();
	}
	
	public PresentationWidget getPresentation() {
		return this.workspace.getPresentation();
	}
	
	public PreviewWidget getPreview() {
		return this.workspace.getPreview();
	}
	
	public AddModulePageWidget getAddModule() {
		return this.workspace.getAddModulePage();
	}
	
	public AddWCAGWidget getAddWCAG() {
		return this.workspace.getAddWCAG();
	}
	
	public ItemsEditorWidget getItemsEditor() {
		return this.workspace.getItemsEditor();
	}
	
	public StaticItemsEditorWidget getStaticItemsEditor() {
		return this.workspace.getStaticItemsEditor();
	}
	
	public SelectTemplateWidget getSelectTemplate() {
		return this.workspace.getSelectTemplate();
	}
	
	public SelectPageWidget getSelectPage() {
		return this.workspace.getSelectPage();
	}
	
	public PagesWidget getPages() {
		return this.workspace.getPages();
	}
	
	public HeaderMenuWidget getHeaderMenu() {
		return this.workspace.getHeaderMenu();
	}
	
	public BlocksEditorWidget getBlocksEditor() {
		return this.workspace.getBlocksEditor();
	};
	
	public MenuWidget getMenu() {
		return this.workspace.getMenu();
	}
	
	public PropertiesWidget getProperties() {
		return this.workspace.getProperties();
	}
	
	public ModulesWidget getModules() {
		return this.workspace.getModules();
	}
	
	public StylesWidget getStyles() {
		return this.workspace.getStyles();
	}
	
	public NotificationsWidget getNotifications() {
		return this.workspace.getNotifications();
	}
	
	public ModalsWidget getModals() {
		return this.workspace.getModals();
	}

	public SettingsWidget getSettings() {
		return this.workspace.getSettings();
	}
	
	public EditCSSWidget getEditCSS() {
		return this.workspace.getEditCSS();
	}
	
	public PresentationLoadingWidget getPresentationLoading() {
		return this.workspace.getPresentationLoading();
	}

	public LayoutEditorWidget getLayoutEditor() {
		return this.workspace.getLayout();
	}
	
	public HTMLEditorWidget getHTMLEditor() {
		return this.workspace.getHTMLEditor();
	}
	
	public TextEditorWidget getTextEditor() {
		return this.workspace.getTextEditor();
	}
	
	public FavouriteModulesListWidget getFavouriteModules() {
		return this.workspace.getFavouriteModules();
	}

	
	public String getActualIdLayout() {
		return this.workspace.getProperties().getSelectedLayoutId(); 
	}
	
	public void setModule(IModuleModel module) {
		this.getProperties().setModule(module);
		this.getPresentation().setModule(module);
		this.getModules().clearSelection();
		this.getModules().setModule(module);
		this.getStyles().setModule(module);
	}
	
	public void showPreview(String previewURL) {
		PreviewWidget preview = this.getPreview();
		String id = getActualIdLayout(); 
		preview.setIdLayout(id);
		preview.setURL(previewURL);
		
		this.showLoadingPresentation();
		
		if (this.getEditCSS().isVisible()) {
			this.getEditCSS().hide();
			this.cssEditorIsOpen = true;
		}
		preview.show();		
	}
	
	public void hidePreview() {
		this.getPreview().hide();
		
		if(this.cssEditorIsOpen) {
			this.getEditCSS().show();
			this.cssEditorIsOpen = false;
		}		
		
		this.hideLoadingPresentation();
	}

	public SemiResponsiveLayoutsWidget getEditSemiResponsiveLayouts() {
		return this.workspace.getEditSemiResponsiveLayouts();
	}
}
