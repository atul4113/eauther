package com.lorepo.iceditor.client.module.sourcelist;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icplayer.client.module.sourcelist.SourceListModule;
import com.lorepo.icplayer.client.module.sourcelist.SourceListView;

public class SourceListPreview extends Composite{

	private SourceListModule module;
	
	public SourceListPreview(SourceListModule module, IEditorServices services) {
		this.module = module;
		
		initWidget(getView());
	}
	
	
	private Widget getView() {
	
		SourceListView view = new SourceListView(module, true);

		for(int i = 0; i < module.getItemCount(); i++){
			String item = module.getItem(i);
			view.addItem("id-"+i, item, false);
		}
		
		return view;
	}
	
}
