package com.lorepo.iceditor.client.controller;

import java.util.HashMap;
import java.util.Set;

import com.lorepo.iceditor.client.IEditorController;
import com.lorepo.iceditor.client.actions.api.IActionService;
import com.lorepo.icplayer.client.PlayerConfig;
import com.lorepo.icplayer.client.content.services.AssetsService;
import com.lorepo.icplayer.client.content.services.ScoreService;
import com.lorepo.icplayer.client.content.services.StateService;
import com.lorepo.icplayer.client.model.Content.ScoreType;
import com.lorepo.icplayer.client.module.api.IPresenter;
import com.lorepo.icplayer.client.module.api.player.IAssetsService;
import com.lorepo.icplayer.client.module.api.player.IContent;
import com.lorepo.icplayer.client.module.api.player.IPage;
import com.lorepo.icplayer.client.module.api.player.IReportableService;
import com.lorepo.icplayer.client.module.api.player.IScoreService;
import com.lorepo.icplayer.client.module.api.player.IStateService;
import com.lorepo.icplayer.client.module.api.player.ITimeService;
import com.lorepo.icplayer.client.ui.PlayerView;


public class EditorPreviewServices implements IEditorController {

	private IActionService 		actionServices;
	private ScoreService scoreService;
	private StateService stateService;
	private AssetsService assetsService;
	private int currentPageIndex;
	
	
	public EditorPreviewServices(IActionService services) {
	
		this.actionServices = services;
		scoreService = new ScoreService(ScoreType.last);
		stateService = new StateService();
		assetsService = new AssetsService(getModel());
	}
	
	
	@Override
	public IScoreService getScoreService() {

		return 	scoreService;
	}

	@Override
	public IContent getModel() {
		return actionServices.getModel();
	}


	@Override
	public int getCurrentPageIndex() {
		return currentPageIndex;
	}
	
	/**
	 * This method is used only in Editor because it is used to show page
	 */
	@Override
	public void setCurrentPageIndex(int index) {
		this.currentPageIndex = index;
	}


	@Override
	public IStateService getStateService() {
		return stateService;
	}


	@Override
	public void switchToPage(String pageName) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void switchToPrevPage() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void switchToNextPage() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public long getTimeElapsed() {
		// TODO Auto-generated method stub
		return 0;
	}


	@Override
	public PlayerView getView() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void closePopup() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void sendAnalytics(String event, HashMap<String, String> params) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public boolean isBookMode() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public boolean hasCover() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public void switchToPage(int index) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void switchToPageById(String pageId) {
		// TODO Auto-generated method stub
		
	}
	
	
	@Override
	public boolean isPopupEnabled() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public void setPopupEnabled(boolean enabled) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public IPresenter findHeaderModule(String name) {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public IPresenter findFooterModule(String name) {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public IAssetsService getAssetsService() {
		return assetsService;
	}


	@Override
	public PlayerConfig getPlayerConfig() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void switchToCommonPage(String commonPageName) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public ITimeService getTimeService() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void showPopup(String pageName, String top, String left,
			String additionalClasses) {
		// TODO Auto-generated method stub
		
	}


	@Override
	public void fireOutstretchHeightEvent() {
		// TODO Auto-generated method stub
		
	}


	@Override
	public int getIframeScroll() {
		// TODO Auto-generated method stub
		return 0;
	}


	@Override
	public IReportableService getReportableService() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public void switchToLastVisitedPage() {
		// TODO Auto-generated method stub
		
	}

	public void switchToCommonPageById(String id) {
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
		return Integer.toString(this.currentPageIndex) + Long.toString(System.currentTimeMillis());
	}


	@Override
	public String getLang() {
		// TODO Auto-generated method stub
		return null;
	}


	@Override
	public boolean isPlayerInCrossDomain() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public Set<IPage> getVisitedPages() {
		// TODO Auto-generated method stub
		return null;
	}
}
