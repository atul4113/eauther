package com.lorepo.iceditor.client.utils.styleeditor;

import com.lorepo.icplayer.client.framework.module.IStyleListener;
import com.lorepo.icplayer.client.framework.module.IStyledModule;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.semi.responsive.SemiResponsiveStyles;

import java.util.Set;

public class StyledModuleMockup implements IStyledModule {
	
	private String classNamePrefix = "";

	@Override
	public void addStyleListener(IStyleListener listener) {}

	@Override
	public String getInlineStyle() {
		return null;
	}

	@Override
	public String getStyleClass() {
		return null;
	}

	@Override
	public void setInlineStyle(String inlineStyle) {}

	@Override
	public void setStyleClass(String styleClass) {}

	@Override
	public String getClassNamePrefix() {
		return classNamePrefix;
	}

	@Override
	public void syncSemiResponsiveStyles(Set<PageLayout> actualLayouts) {
		
	}

	public void setClassNamePrefix(String classNamePrefix) {
		this.classNamePrefix = classNamePrefix;
	}


	public SemiResponsiveStyles getSemiResponsiveStyles() {
		// TODO Auto-generated method stub
		return null;
	}
	
	
}
