package com.lorepo.iceditor.client.module;

import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.module.ModuleFactory;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ModuleEditor {

	protected static final int TAB_WIDTH = 770;
	protected static final int TAB_HEIGHT = 490;
	
	private IEditorServices editorServices;
	private IModuleModel			module;

	
	/**
	 * Constructor
	 * @param module
	 */
	public ModuleEditor(IModuleModel module) {
		
		this.module = module;
	}
	
	
	public ModuleEditor(IModuleModel module, IEditorServices services) {
		
		this.module = module;
		this.editorServices = services;
	}


	/**
	 * Get module
	 * @return
	 */
	public IModuleModel getModule(){
		return module;
	}
	
	/**
	 * Get editor services
	 * @return
	 */
	public IEditorServices getServices(){
		return editorServices;
	}
	
	/**
	 * Get view for PageEditor
	 * @return
	 */
	public Widget getView(){
		
		ModuleFactory moduleFactory = new ModuleFactory(null);
		return (Widget) moduleFactory.createView(module);
	}
	
	
	public boolean hasEditorWidget(){
		return false;
	}
	
	/**
	 * @return tytul edytor dlg
	 */
	public String getDlgEditorTitle(){
		return DictionaryWrapper.get("module_editor");
	}
	
	/**
	 * Get tab for given index
	 * @param index
	 * @return
	 */
	public Widget getEditorWidget(){

		return null;
	}

	/**
	 * Save all temporary data into model
	 */
	public void save() {
	}

}
