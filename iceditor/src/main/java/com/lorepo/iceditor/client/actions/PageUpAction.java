package com.lorepo.iceditor.client.actions;

import com.lorepo.iceditor.client.controller.AppController;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.model.page.PageList;
import com.lorepo.icplayer.client.module.api.player.IChapter;
import com.lorepo.icplayer.client.module.api.player.IContentNode;

public class PageUpAction extends NavigationButtons{

	public PageUpAction(AppController controller) {
		super(controller);
	}

	public static native boolean isPrevChapterExpanded(boolean isChapter) /*-{
	  var chapter = null;
	  if (isChapter){
	  	chapter = $wnd.$('.listChapter.selected').prev();
	  }else{
	  	chapter = $wnd.$('.listItem.selected').prev();
	  }
	  return chapter.hasClass('expanded');
	}-*/;

	@Override
	public void execute() {
		super.execute();

		executeStart();
		
		if(index > 0) {
			IContentNode nodeAbove = currentChapter.get(index-1);
			if(nodeAbove instanceof PageList) {
				boolean isChapter = false;
				if(currentNode instanceof PageList) {
					isChapter = true;
				}
				if(!isPrevChapterExpanded(isChapter)) {
					movePageUp(index);
					controller.getAppFrame().getPages().doExpandToSelected();
					return;
				}
				chapterToMove = (IChapter) nodeAbove;
				chapterToMove.add(currentNode);
				currentChapter.remove(currentNode);
				refreshAfterModification();
				return;
			}
		}
		
		if (index > 0) {
			movePageUp(index);
			controller.getAppFrame().getPages().doExpandToSelected();
		} else if (chapterToMove != null) { // index == 0
			// chapterToMove is null in case when page is last in list; then we don't have to do anything
			chapterToMove.addOnIndex(currentChapterIndex, currentNode);

			removeFromTree();
			refreshAfterModification();
		}
	}
}
