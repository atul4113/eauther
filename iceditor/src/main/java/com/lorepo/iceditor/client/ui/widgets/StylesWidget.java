package com.lorepo.iceditor.client.ui.widgets;

import static com.google.gwt.query.client.GQuery.$;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AnchorElement;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.OptionElement;
import com.google.gwt.dom.client.SelectElement;
import com.google.gwt.dom.client.TextAreaElement;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.EventListener;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.actions.AbstractAction;
import com.lorepo.iceditor.client.actions.ActionFactory;
import com.lorepo.iceditor.client.actions.ActionFactory.ActionType;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.iceditor.client.utils.ui.styleeditor.CssParser;
import com.lorepo.iceditor.client.utils.ui.styleeditor.StyleEditorPresenterUtils;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.framework.module.IStyledModule;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.group.Group;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.icplayer.client.module.button.ButtonModule;

public class StylesWidget extends Composite {

	private static StylesWidgetUiBinder uiBinder = GWT
			.create(StylesWidgetUiBinder.class);

	interface StylesWidgetUiBinder extends UiBinder<Widget, StylesWidget> {}
	
	@UiField AnchorElement updateStyles;
	@UiField TextAreaElement inlineCSS;
	@UiField SelectElement cssClass;
	@UiField HTMLPanel stylesWidget;
	private IModuleModel currentModule;
	private Group currentGroup; 
	private Page currentPage;
	private List<String> classNames = new ArrayList<String>();
	
	private AbstractAction onPageStylesChanged;
	private AbstractAction onModuleStylesChanged;

	public StylesWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		connectHandlers();
		updateElementsTexts();
	}

	private void connectHandlers() {
		Event.sinkEvents(this.cssClass, Event.ONCHANGE);
		Event.setEventListener(this.cssClass, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCHANGE != event.getTypeInt()) {
					return;
				}
				
				String className = cssClass.getValue();
				if (className.trim().isEmpty()) {
					className = "";
				}
				
				if (currentPage != null) {
					currentPage.setStyleClass(className);
					onPageStylesChanged.execute();
				} else if (currentModule != null) {
					currentModule.setStyleClass(className);
					onModuleStylesChanged.execute();
				} else if(currentGroup != null) {
					currentGroup.setStyleClass(className);
					onModuleStylesChanged.execute();
				}
				
				cssClass.blur();
			}
		});
		
		Event.sinkEvents(this.updateStyles, Event.ONCLICK);
		Event.setEventListener(this.updateStyles, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if(Event.ONCLICK != event.getTypeInt()) {
					return;
				}
				
				String inlineStyle = inlineCSS.getValue().replace("\n", "");
				inlineStyle = deletePositionImportantStyles(inlineStyle);
				inlineCSS.setValue(prepareStringToView(inlineStyle));
				inlineStyle = inlineStyle.replace("\n", "");
				if (currentPage != null) {
					currentPage.setInlineStyle(inlineStyle);
					onPageStylesChanged.execute();
				} else if (currentModule != null) {
					currentModule.setInlineStyle(inlineStyle);
					onModuleStylesChanged.execute();
				}else if(currentGroup != null) {
					currentGroup.setInlineStyle(inlineStyle);
					onModuleStylesChanged.execute();
				}
			}
		});
		
		Event.sinkEvents(this.inlineCSS, Event.FOCUSEVENTS);
		Event.setEventListener(this.inlineCSS, new EventListener() {
			@Override
			public void onBrowserEvent(Event event) {
				if (Event.ONFOCUS == event.getTypeInt()) {
					WidgetLockerController.disableKeysAction();
				} else if (Event.ONBLUR == event.getTypeInt()) {
					WidgetLockerController.enableKeysAction();
				}
			}
		});
	}
	
	public String prepareStringToView (String inlineStyle) {
		StringBuilder strBuilder = new StringBuilder();
		String[] attributes = inlineStyle.split(";");
		for (String attribute: attributes) {
			if(!attribute.equals("")){
				strBuilder.append(attribute);
				strBuilder.append(";");
				strBuilder.append("\n");
			}
		}
		
		return strBuilder.toString();
	}
	
	public String deletePositionImportantStyles (String inlineStyle) {
		String[] attributes = inlineStyle.split(";");
		StringBuilder strBuilder = new StringBuilder();
		for (String attribute: attributes) {
			if((attribute.contains("left") || attribute.contains("top") 
					|| attribute.contains("right") || attribute.contains("bottom")) && (!attribute.contains("-left") && !attribute.contains("-top") 
					&& !attribute.contains("-right") && !attribute.contains("-bottom")
					&& !attribute.contains("text-align") && !attribute.contains("vertical-align") && !attribute.contains("background") && !attribute.contains("gradient"))){
				continue;
			}
			if(!attribute.replaceAll("\\s","").equals("")){
				strBuilder.append(attribute);
				strBuilder.append(";");
			}
		}
		
		String newAttributes = strBuilder.toString();
		return newAttributes;
	}
	
	public void setActionFactory(ActionFactory actionFactory) {
		onPageStylesChanged = actionFactory.getAction(ActionType.pageStylesChanged);
		onModuleStylesChanged = actionFactory.getAction(ActionType.moduleStylesChanged);
	}

	public void setModule(IModuleModel module) {
		if (module != null && currentModule != null && currentModule.getId().equals(module.getId())) {
			return;
		}
		
		currentPage = null;
		currentGroup = null; 
		currentModule = module;
		
		updateStyledModuleClassesList(currentModule);
		updateStyledModuleInlineStyle(currentModule);
	}
	
	public void setGroup(Group group) {
		if (group != null && currentGroup != null && currentGroup.getId().equals(group.getId())) {
			return;
		}
		currentPage = null;
		currentGroup = group; 
		currentModule = null;
		updateStyledModuleClassesList(currentGroup);
		updateStyledModuleInlineStyle(currentGroup);
	}

	private void updateStyledModuleInlineStyle(IStyledModule module) {
		this.inlineCSS.setValue(module == null ? "" : module.getInlineStyle().replace(";", ";\n"));
	}
	
	private ArrayList<String> getSuitableClasses(IStyledModule module) {
		ArrayList<String> names = new ArrayList<String>();
		String prefix = StyleEditorPresenterUtils.getModuleClassNamePrefix(module);
		String moduleCssClass = module.getStyleClass();
		
		boolean found = false;
		
		names.add(" ");
		
		for (String name : classNames){
			String lowerCaseName = name.toLowerCase();

			boolean shouldAddButtonClass = StyleEditorPresenterUtils.shouldAddButtonClass(lowerCaseName, prefix);
			
			if (module instanceof ButtonModule && shouldAddButtonClass) {
				names.add(name);
			} else if(lowerCaseName.startsWith(prefix) && !lowerCaseName.equals(prefix)) {
				names.add(name);
				if(moduleCssClass != null && name.compareTo(moduleCssClass) == 0){
					found = true;
				}
			}
		}
		
		// if lesson css does not contain previously assigned css style to module, add it
		if (!found && moduleCssClass != null && !moduleCssClass.isEmpty()) {
			names.add(moduleCssClass);
		}
		
		return names;
	}

	private void updateStyledModuleClassesList(IStyledModule module) {
		cssClass.clear();
		
		if (module == null) {
			return;
		}
		
		ArrayList<String> names = getSuitableClasses(module);
	
		for (String className : names) {
			OptionElement optionElement = Document.get().createOptionElement();

			optionElement.setValue(className);
			optionElement.setText(className);
			optionElement.setSelected(module.getStyleClass().equals(className));
			
			cssClass.add(optionElement, null);
		}
	}
	
	public void setCSS(String css){
		CssParser parser = new CssParser();
		classNames = parser.findClasses(css);
	}

	public void setPage(Page page) {
		if (currentPage != null && currentPage.getId().equals(page.getId())) {
			return;
		}
		currentGroup = null; 
		currentModule = null;
		currentPage = page;
		
		updateStyledModuleInlineStyle(page);
		updateStyledModuleClassesList(page);
	}
	
	public void updateElementsTexts() {
		updateStyles.setInnerText(DictionaryWrapper.get("update_style"));
		$(stylesWidget).find(".boxName").text(DictionaryWrapper.get("styles"));
		
		GQuery el = $(stylesWidget).find(".property-cssClass");
		
		el.eq(0).find(".stylesLabel").text(DictionaryWrapper.get("css_class"));
		el.eq(1).find(".stylesLabel").text(DictionaryWrapper.get("inline_css"));
	}

	public void refresh() {
		IStyledModule currentStyledModule;
		
		if (currentModule != null) {
			currentStyledModule = currentModule;
		} else if (currentPage != null) {
			currentStyledModule = currentPage;
		} else if (currentGroup != null) {
			currentStyledModule = currentGroup;	
		} else {
			return;
		}

		updateStyledModuleInlineStyle(currentStyledModule);
		updateStyledModuleClassesList(currentStyledModule);
	}
}
