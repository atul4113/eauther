package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.actions.api.IAppController;
import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;

public class NavigationButtons extends AbstractAction{

	public IAppController controller = null;
	public IContentNode currentNode = null;
	public IChapter chapter = null;
	public PageList pages = null;
	public int index = -1;
	
	public void execute() {
        controller = getServices().getAppController();
        currentNode = controller.getSelectionController().getSelectedContent();
        chapter = getModel().getParentChapter(currentNode);
        pages = (PageList) chapter;
	}
	
	public NavigationButtons(AppController controller) {
		super(controller);
	}

	public void switchToPage(Page page) {
		controller.switchToPage(page, false);
	}
	
	public void switchToChapter(IChapter chapter) {
		controller.switchToChapter(chapter);
	}
	
	public void refreshContentList() {
		controller.getAppFrame().getPages().refresh();
		
		controller.getAppFrame().getPages().setSelectedNode(currentNode);
	}
	
	public void save() {
		controller.saveContent();
	}
	
	public void movePageUp(int index) {
		if(chapter instanceof PageList){
			pages.movePage(index, index-1);
			switchItem();
		}
	}

	public void movePageDown(int index) {
		if(chapter instanceof PageList){
			pages.movePage(index, index+1);
			switchItem();
		}
	}
	
	public void switchItem() {
		if (currentNode instanceof Page) {
			switchToPage((Page) currentNode);
		} else if (currentNode instanceof IChapter) {
			switchToChapter((IChapter) currentNode);
		}
		
		save();
		refreshContentList();
	}
	
	public int getCurrentIndex() {
		return pages.indexOf(currentNode);
	}


	// ------------ Common for PageUpAction and PageDownAction

	protected IChapter chapterToMove;
	protected int currentChapterIndex;
	protected PageList currentChapter;

	protected void executeStart() {
		index = pages.indexOf(currentNode);
		chapterToMove = null;
		currentChapterIndex = 0;

		Content content = getServices().getModel();
		currentChapter = getCurrentChapter();
		if(currentNode instanceof PageList) {
			currentChapter = (PageList) content.getParentChapter(currentChapter);
		}

		// if the name of currentChapter is blank, then we are handling node that doesn't belong to any chapter
		if(currentChapter.getName() != "") {
			chapterToMove = content.getParentChapter(currentChapter);
			if (chapterToMove != null) {
				currentChapterIndex = chapterToMove.indexOf(currentChapter);
			}
		}

	}

	protected void refreshAfterModification() {
		controller.getAppFrame().getPages().refresh();

		if (currentNode instanceof PageList) {
			controller.switchToChapter((IChapter) currentNode);
			getServices().getAppController().getAppFrame().getPages().selectChapter((IChapter) currentNode);
		} else {
			controller.switchToPage((Page) currentNode, false);
		}

		controller.getAppFrame().getPages().doExpandToSelected();
		controller.saveContent();
	}

	protected void removeFromTree()
	{
		if (currentNode instanceof PageList) {
			currentChapter.removeFromTree(currentNode, true);
		} else {
			currentChapter.remove(currentNode);
		}
	}


}
