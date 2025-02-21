package com.lorepo.iceditor.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.EditorConfig;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.semi.responsive.ui.widgets.SemiResponsiveLayoutsWidget;
import com.lorepo.iceditor.client.ui.widgets.content.AddWCAGWidget;
import com.lorepo.iceditor.client.ui.widgets.content.EditCSSWidget;
import com.lorepo.iceditor.client.ui.widgets.content.FavouriteModulesListWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PageLoadingWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationLoadingWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PresentationWidget;
import com.lorepo.iceditor.client.ui.widgets.content.PreviewWidget;
import com.lorepo.iceditor.client.ui.widgets.content.SettingsWidget;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.ui.widgets.docs.DocViewerWidget;
import com.lorepo.iceditor.client.ui.widgets.modals.ModalsWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.ModulesWidget;
import com.lorepo.iceditor.client.ui.widgets.modules.add.AddModulePageWidget;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationType;
import com.lorepo.iceditor.client.ui.widgets.notification.NotificationsWidget;
import com.lorepo.iceditor.client.ui.widgets.pages.PagesWidget;
import com.lorepo.iceditor.client.ui.widgets.pages.select.SelectPageWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.PropertiesWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.BlocksEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.ConnectorBlocksEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.FileSelectorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.HTMLEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.ItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.LayoutEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.StaticItemsEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.properties.editors.TextEditorWidget;
import com.lorepo.iceditor.client.ui.widgets.templates.SelectTemplateWidget;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;

public class WorkspaceWidget extends Composite {

	private static WorkspaceWidgetUiBinder uiBinder = GWT
			.create(WorkspaceWidgetUiBinder.class);

	interface WorkspaceWidgetUiBinder extends UiBinder<Widget, WorkspaceWidget> {
	}
	
	@UiField HTMLPanel panel;
	@UiField HeaderWidget header;
	@UiField HeaderMenuWidget headerMenu;
	@UiField MenuWidget menu;
	@UiField PagesWidget pages;
	@UiField ModulesWidget modules;
	@UiField PropertiesWidget properties;
	@UiField StylesWidget styles;
	@UiField NotificationsWidget notifications;
	@UiField ModalsWidget modals;
	
	// Content
	@UiField SimplePanel content;
	@UiField SettingsWidget settings;
	@UiField AddWCAGWidget addWCAG;
	@UiField SemiResponsiveLayoutsWidget semiResponsiveLayouts;
	@UiField EditCSSWidget editCSS;
	@UiField PresentationWidget presentation;
	@UiField PreviewWidget preview;
	@UiField PresentationLoadingWidget presentationLoading;
	@UiField PageLoadingWidget pageLoading;
	@UiField LayoutEditorWidget layoutEditor;

	@UiField AddModulePageWidget addModule;
	@UiField SelectTemplateWidget selectTemplate;
	@UiField SelectPageWidget selectPage;
	
	@UiField TextEditorWidget textEditor;
	@UiField ConnectorBlocksEditorWidget connectorBlocksEditor;
	@UiField HTMLEditorWidget htmlEditor;
	@UiField ItemsEditorWidget itemsEditor;
	@UiField StaticItemsEditorWidget staticItemsEditorWidget;
	
	@UiField FileSelectorWidget fileSelector;
	
	@UiField FavouriteModulesListWidget favouriteModules;
	
	@UiField DocViewerWidget docViewer;
	
	private AbstractAction onSaveAction;
	private AbstractAction onAddModuleAction;
	private AbstractAction onRemoveModuleAction;
	private AbstractAction onCopyAction;
	private AbstractAction onPasteAction;
	private AbstractAction onUndoAction;
	private AbstractAction onRedoAction;

	public WorkspaceWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("editorContainer");
		content.getElement().setId("content");
		
		properties.setTextEditor(getTextEditor());
		properties.setBlocksEditor(getBlocksEditor());
		properties.setHTMLEditor(getHTMLEditor());
		properties.setItemsEditor(getItemsEditor());
		properties.setFileSelector(getFileSelector());
		properties.setLayoutEditor(getLayout());
		properties.setDocViewer(getDocViewer());
		properties.setStaticItemsEditor(this.getStaticItemsEditor());
		presentation.setPropertiesWidget(properties);
		
		getItemsEditor().setFileSelector(getFileSelector());
		this.getStaticItemsEditor().setFileSelector(getFileSelector());
		
		
		addKeyboardHandlers(this);
		
		notifications.addOneTimeMessage(DictionaryWrapper.get("header_footer_notification"), NotificationType.notice, true, "set_header_notification");
	}
	
	public void setEditorConfig(EditorConfig config) {
		menu.setEditorConfig(config);
	}
	
	public SimplePanel getContentWrapper() {
		return content;
	}

	public HeaderWidget getHeader() {
		return header;
	}
	
	public HeaderMenuWidget getHeaderMenu() {
		return headerMenu;
	}
	
	public MenuWidget getMenu() {
		return menu;
	}
	
	public PagesWidget getPages() {
		return pages;
	}

	public ModulesWidget getModules() {
		return modules;
	}
	
	public PropertiesWidget getProperties() {
		return properties;
	}
	
	public StylesWidget getStyles() {
		return styles;
	}

	public NotificationsWidget getNotifications() {
		return notifications;
	}

	public ModalsWidget getModals() {
		return modals;
	}
	
	/** CONTENT GETTERS */
	public PresentationWidget getPresentation() {
		return presentation;
	}
	
	public PreviewWidget getPreview() {
		return preview;
	}
	
	public PresentationLoadingWidget getPresentationLoading() {
		return presentationLoading;
	}
	
	public PageLoadingWidget getPageLoading() {
		return pageLoading;
	}
	
	public AddModulePageWidget getAddModulePage() {
		return addModule;
	}
	
	public TextEditorWidget getTextEditor() {
		return textEditor;
	}
	
	public BlocksEditorWidget getBlocksEditor() {
		return connectorBlocksEditor;
	}
	
	public HTMLEditorWidget getHTMLEditor() {
		return htmlEditor;
	}
	
	public ItemsEditorWidget getItemsEditor() {
		return itemsEditor;
	}
	
	public StaticItemsEditorWidget getStaticItemsEditor() {
		return this.staticItemsEditorWidget;
	}
	
	public FileSelectorWidget getFileSelector() {
		return fileSelector;
	}
	
	public DocViewerWidget getDocViewer() {
		return docViewer;
	}
	
	public SelectTemplateWidget getSelectTemplate() {
		return selectTemplate;
	}
	
	public SelectPageWidget getSelectPage() {
		return selectPage;
	}
	
	public SettingsWidget getSettings() {
		return settings;
	}
	
	public AddWCAGWidget getAddWCAG() {
		return addWCAG;
	}
	
	public LayoutEditorWidget getLayout() {
		return layoutEditor;
	}
	
	public SemiResponsiveLayoutsWidget getSemiResponsiveLayoutsPanel() {
		return this.semiResponsiveLayouts;
	}
	
	public EditCSSWidget getEditCSS() {
		return editCSS;
	}
	
	public FavouriteModulesListWidget getFavouriteModules() {
		return favouriteModules;
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onSaveAction = actionFactory.getAction(ActionType.save);
		onAddModuleAction = actionFactory.getAction(ActionType.addModule);
		onRemoveModuleAction = actionFactory.getAction(ActionType.removeModule);
		onCopyAction = actionFactory.getAction(ActionType.copy);
		onPasteAction = actionFactory.getAction(ActionType.paste);
		onUndoAction = actionFactory.getAction(ActionType.undo);
		onRedoAction = actionFactory.getAction(ActionType.redo);
	}
	
	private native void addKeyboardHandlers(WorkspaceWidget workspace) /*-{
		var KEY_CODES = {
			Delete: 46,
			C: 67,
			M: 77,
			S: 83,
			V: 86,
			Y: 89,
			Z: 90
		};
		
		function keyboardEventsCallback(event) {
			var code = event.keyCode || event.which,
				action = null;
			
			if (workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::isWidgetLockerVisible()()) {
				return;
			}
			
			if (!event.ctrlKey && !event.metaKey) {
				// Neither Ctrl nor Command (OS X) keys were down when new key was pressed.
				
				if (code != KEY_CODES.Delete) {
					return;
				}
				
				action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onRemoveModuleAction;
			}
			
			switch(code) {
				case KEY_CODES.S:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onSaveAction;
					break;
				case KEY_CODES.M:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onAddModuleAction;
					break;
				case KEY_CODES.Z:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onUndoAction;
					break;
				case KEY_CODES.Y:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onRedoAction;
					break;
				case KEY_CODES.C:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onCopyAction;
					break;
				case KEY_CODES.V:
					action = workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::onPasteAction;
					break;
			}
			
			if (action) {
				// Keyboard shortcuts should be disabled when document is focues on elements related to forms.
				// Without ommition shortcuts will override basic functionalities like copying and pasting text.
				// Below list source: http://www.w3.org/TR/html-markup/elements.html
				var OMMITED_TYPES = ['text', 'password', 'checkbox', 'radio', 'button', 'submit', 'reset', 'file',
					'hidden', 'image', 'datetime', 'datetime-local', 'date', 'month', 'time', 'week', 'number',
					'range', 'email', 'url', 'search', 'tel', 'color', 'select-one', 'textarea', 'iframe'];
				
				if ($wnd.$.inArray($doc.activeElement.type, OMMITED_TYPES) != -1) {
					return;
				}

				event.preventDefault();
				
				workspace.@com.lorepo.iceditor.client.ui.widgets.WorkspaceWidget::executeAction(Lcom/lorepo/iceditor/client/actions/AbstractAction;)(action);
				
				return false;
			}
		}
		
		$wnd.$($doc).on('keydown', keyboardEventsCallback);
		
		$wnd.offKeyboardEventsCallback = function () {
			$wnd.$($doc).off('keydown', keyboardEventsCallback);
		}
		
		$wnd.onKeyboardEventsCallback = function () {
			$wnd.$($doc).off('keydown', keyboardEventsCallback);
			$wnd.$($doc).on('keydown', keyboardEventsCallback);
		}
	}-*/;
	
	private void executeAction(AbstractAction action) {
		action.execute();
	}
	
	private boolean isWidgetLockerVisible() {
		return WidgetLockerController.isVisible();
	}

	public SemiResponsiveLayoutsWidget getEditSemiResponsiveLayouts() {
		return this.semiResponsiveLayouts;
	}
}
