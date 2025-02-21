package com.lorepo.iceditor.client.ui.page;

import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icplayer.client.model.Content;

public class EditorServicesImpl implements  IEditorServices{

	private Content content;
	
	/**
	 * Constructor
	 * @param content
	 */
	public EditorServicesImpl(Content content){
		
		this.content = content;
	}
	
	
	@Override
	public Content getContent() {
		
		return content;
	}

}
