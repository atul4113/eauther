package com.lorepo.iceditor.client.actions;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.ui.Ruler;

public class UpdateRulersPositionsAction  extends AbstractPageAction {
	private AppController appController;

	public UpdateRulersPositionsAction(AppController controller) {
		super(controller);
		this.appController = controller;
	}
	
	public void execute(List<Integer> verticals, List<Integer> horizontals) {
		Page page = appController.getCurrentPage();
		List<Ruler> verticalRulers = new ArrayList<Ruler>();
		List<Ruler> horizontalRulers = new ArrayList<Ruler>();
		
		for (int position : verticals) {	
			verticalRulers.add(new Ruler("vertical", position));
		}
		
		for (int position : horizontals) {	
			horizontalRulers.add(new Ruler("horizontal", position));
		}
		
		page.setRulers(verticalRulers, horizontalRulers);
		appController.getModyficationController().setModified(true);
	}
}
