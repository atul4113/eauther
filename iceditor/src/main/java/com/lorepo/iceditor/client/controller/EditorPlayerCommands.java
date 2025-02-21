package com.lorepo.iceditor.client.controller;

import com.lorepo.icplayer.client.module.api.player.IPlayerCommands;
import com.lorepo.icplayer.client.module.api.player.PageScore;
import com.lorepo.icplayer.client.page.PageController;

public class EditorPlayerCommands implements IPlayerCommands {

	private PageController	pageController;
	
	
	public EditorPlayerCommands(PageController pageController){
	
		this.pageController = pageController;
	}
	
	
	@Override
	public void checkAnswers() {

		pageController.checkAnswers();
	}


	@Override
	public void uncheckAnswers() {

		pageController.uncheckAnswers();
	}


	@Override
	public void reset() {
		pageController.resetPageScore();
		pageController.sendResetEvent();
	}

	@Override
	public void resetPageScore() {
		pageController.resetPageScore();
	}
	
	@Override
	public void closePopup() {
	}


	@Override
	public PageScore getCurrentPageScore() {

		return pageController.getPageScore();
	}


	@Override
	public void nextPage() {
	}

	@Override
	public void prevPage() {
	}


	@Override
	public void gotoPage(String pageName) {
	}


	@Override
	public void executeEventCode(String code) {

		pageController.runScript(code);
	}


	@Override
	public void updateCurrentPageScore(boolean incrementCheckCounter) {

		pageController.updateScore(incrementCheckCounter);
	}


	@Override
	public long getTimeElapsed() {
		return 0;
	}


	@Override
	public void gotoPageIndex(int index) {
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public void gotoPageId(String pageId) {
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public void sendPageAllOkOnValueChanged(boolean sendEvent) {
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public void setNavigationPanelsAutomaticAppearance(boolean sendEvent) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void showNavigationPanels(){
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public void hideNavigationPanels(){
		// TODO Auto-generated method stub
		
	}
	
	@Override
	public PageController getPageController() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void incrementCheckCounter() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void increaseMistakeCounter() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void gotoCommonPage(String commonsPageName) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void showPopup(String pageName, String top, String left,
			String additionalClasses) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void updateCurrentPageScoreWithMistakes(int mistakes) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public int getIframeScroll() {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public void goToLastVisitedPage() {

    }
	
	@Override
	public void changeHeaderVisibility(boolean isVisible) {
		
	}
	
	@Override
	public void changeFooterVisibility(boolean isVisible) {
		
	}


	@Override
	public void gotoCommonPageId(String id) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void enableKeyboardNavigation() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void disableKeyboardNavigation() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public String getPageStamp() {
		// TODO Auto-generated method stub
		return null;
	}
}
