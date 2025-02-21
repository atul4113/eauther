package com.lorepo.iceditor.client.ui.page;

import com.google.gwt.dom.client.Style;
import com.lorepo.iceditor.client.module.addon.AddonPreview;
import com.lorepo.icf.uidesigner.ItemView;
import com.lorepo.icf.utils.StringUtils;
import com.lorepo.icplayer.client.module.api.ILayoutDefinition;
import com.lorepo.icplayer.client.module.api.IModuleModel;

public class ProxyWidget extends ItemView<IModuleModel>{
	
	private int maxScore = 0;
	private AddonPreview addonPreview = null;

	public ProxyWidget(IModuleModel module){
		super(module);
	}
	
	@Override
	public int getLeft() {
		return getModel().getLeft();
	}

	@Override
	public int getTop() {
		return getModel().getTop();
	}

	@Override
	public int getWidth() {
		return getModel().getWidth();
	}

	@Override
	public int getHeight() {
		return getModel().getHeight();
	}

	@Override
	public void move(int dx, int dy){
		IModuleModel model = getModel();
		ILayoutDefinition layout = model.getLayout();
		if(layout.hasLeft()){
			model.setLeft(model.getLeft()+dx);
		}
		if(layout.hasRight()){
			model.setRight(model.getRight()-dx);
		}
		
		if(layout.hasTop()){
			model.setTop(model.getTop()+dy);
		}
		if(layout.hasBottom()){
			model.setBottom(model.getBottom()-dy);
		}
	}
	
	@Override
	public void resize(int dx, int dy){
		IModuleModel model = getModel();
		ILayoutDefinition layout = model.getLayout();
		if(layout.hasRight()){
			model.setRight(model.getRight()-dx);
		}
		if(layout.hasBottom()){
			model.setBottom(model.getBottom()-dy);
		}
		Style style = getElement().getStyle();
		int width = StringUtils.px2int(style.getProperty("width")) + dx;
		int height = StringUtils.px2int(style.getProperty("height")) + dy;
		
		model.setWidth(width);
		model.setHeight(height);
		setPixelSize(width, height);
	}

	@Override
	public boolean isLocked(){
		return getModel().isLocked();
	}
	
	public void setMaxScore(int maxScore) {
		this.maxScore = maxScore;
	}
	
	public int getMaxScore() {
		if (this.addonPreview != null) {
			return this.addonPreview.getMaxScore();
		}
		
		return maxScore;
	}
	
	public void setAddonPreview (AddonPreview addonPreview) {
		this.addonPreview = addonPreview;
	}
}
