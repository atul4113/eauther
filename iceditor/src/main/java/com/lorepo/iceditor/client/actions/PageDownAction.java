package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class PageDownAction extends NavigationButtons {

	public PageDownAction(AppController controller) {
		super(controller);
	}

	public static native boolean isNextChapterExpanded(boolean isChapter) /*-{
	  var chapter = null;
	  if (isChapter){
	  	chapter = $wnd.$('.listChapter.selected').next();
	  }else{
	  	chapter = $wnd.$('.listItem.selected').next();
	  }
	  return chapter.hasClass('expanded');
	}-*/;

	@Override
	public void execute() {
		super.execute();
		
		executeStart();
		
		if (index >= 0 && index+1 < currentChapter.size()) {
			IContentNode nodeBelow = currentChapter.get(index+1);
			if (nodeBelow instanceof PageList) {
				boolean isChapter = false;
				if (currentNode instanceof PageList) {
					isChapter = true;
				}
				if (!isNextChapterExpanded(isChapter)) {
					movePageDown(index);
					controller.getAppFrame().getPages().doExpandToSelected();
					return;
				}
				chapterToMove = (IChapter) nodeBelow;
				chapterToMove.addOnIndex(0, currentNode);
				currentChapter.remove(currentNode);
				refreshAfterModification();
				return;
			}
		}

		if( index+1 < pages.getPageCount() && index > -1) {
			movePageDown(index);
			controller.getAppFrame().getPages().doExpandToSelected();
		} else if (chapterToMove != null) {
			// chapterToMove is null in case when page is last in list; then we don't have to do anything
			chapterToMove.addOnIndex(currentChapterIndex+1, currentNode);

			removeFromTree();
			refreshAfterModification();
		}	
	}
}