package com.lorepo.iceditor.client.module.report;

import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.module.api.IEditorServices;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.module.api.player.IPage;
import com.lorepo.icplayer.client.module.report.ReportModule;
import com.lorepo.icplayer.client.module.report.ReportView;

public class ReportPreview extends Composite{

	private ReportModule module;
	private IEditorServices services;
	
	
	public ReportPreview(ReportModule module, IEditorServices services) {
		this.module = module;
		this.services = services;
		initWidget(createView());
	}
	
	
	private Widget createView() {
	
		ReportView view = new ReportView(module, true);
		Content content = services.getContent();
		
		for(int i = 0; i < content.getPages().getTotalPageCount(); i++){
		
			IPage page = content.getPage(i);
			if(page.isReportable()){
				view.addRow(page.getName());
			}
		}
		
		view.addSummaryRow(50, 0, 0, 0);
		
		return view;
	}
	
}
