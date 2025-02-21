package com.lorepo.iceditor.client.utils.ui.styleeditor;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.icplayer.client.framework.module.IStyledModule;
import com.lorepo.icplayer.client.module.button.ButtonModule;

public class StyleEditorPresenter{

	public interface IDisplay{
		void setEnabled(boolean enabled);
		void setInlineStyles(String text);
		void clearClassList();
		void setClassList(List<String> classNames);
		void setSelectedClass(String name);
		void addValueChangedListener(IValueChanged listener);
	}
	
	public interface IValueChanged{
		void onClassNameChanged(String newClassName);
		void onInlineStyleChanged(String newInlineStyle);
	}

	private IStyledModule module;
	private IDisplay view;
	private List<String> classNames;
	private IActionService actionService;
	
	
	public StyleEditorPresenter(){
		classNames = new ArrayList<String>();
	}
	
	
	public void setView(IDisplay display){
		view = display;
		
		view.addValueChangedListener(new IValueChanged(){
			@Override
			public void onClassNameChanged(String newClassName) {
				if(module != null){
					module.setStyleClass(newClassName);
					saveUndoState();
				}
			}
			@Override
			public void onInlineStyleChanged(String newInlineStyle) {
				if(module != null){
					module.setInlineStyle(newInlineStyle);
					saveUndoState();
				}
			}
		});
	}
	
	
	protected void saveUndoState() {
		if(actionService != null){
//			actionService.getPageEditor().saveUndoState();
		}
	}


	public void setModule(IStyledModule newModule){
		
		this.module = newModule;
		view.setEnabled(module!=null);
		updateDisplay();
	}

	
	private void updateDisplay() {

		if(view != null){
			view.clearClassList();

			if(module != null){
	
				addClassNamesToDisplay();
				String convertedInlineStyle = module.getInlineStyle().replace(";", ";\n");
				view.setInlineStyles(convertedInlineStyle);
			}
			else{
				view.setInlineStyles("");
			}
		}
	}
	
	private void addClassNamesToDisplay() {

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
		
		view.setClassList(names);
		view.setSelectedClass(moduleCssClass);
	}


	public void setCSS(String css){
		
		CssParser parser = new CssParser();
		classNames = parser.findClasses(css);
		updateDisplay();
	}


	public void setActionService(IActionService as) {
		actionService = as;
	}
}
