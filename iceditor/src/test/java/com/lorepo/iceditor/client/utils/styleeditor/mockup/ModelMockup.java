package com.lorepo.iceditor.client.utils.styleeditor.mockup;

import com.lorepo.icplayer.client.framework.module.IStyleListener;
import java.util.Set;
import com.lorepo.icplayer.client.model.layout.PageLayout;
import com.lorepo.icplayer.client.semi.responsive.SemiResponsiveStyles;
import com.lorepo.icplayer.client.framework.module.IStyledModule;

public class ModelMockup implements IStyledModule {

	private String inlineStyle = "background-color:red;color:yellow;";
	private String moduleName;
	private String className = "";
	
	
	public ModelMockup(String name){
		this.moduleName = name;
	}
	
	
	@Override
	public void addStyleListener(IStyleListener listener) {
	}

	@Override
	public String getInlineStyle() {
		return inlineStyle;
	}

	@Override
	public String getStyleClass() {
		return className;
	}

	@Override
	public void setInlineStyle(String inlineStyle) {
		this.inlineStyle = inlineStyle;
	}

	@Override
	public void setStyleClass(String styleClass) {
		this.className = styleClass;
	}

	@Override
	public String getClassNamePrefix() {
		return moduleName;
	}

	@Override
	public void syncSemiResponsiveStyles(Set<PageLayout> actualLayouts) {
		
	}
	
	public void setCssClass(String className){
		this.className = className;
	}


	public SemiResponsiveStyles getSemiResponsiveStyles() {
		// TODO Auto-generated method stub
		return null;
	}
}
