package com.lorepo.iceditor.client.semi;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SemiResponsiveConfigurationJava implements SemiResponsiveConfiguration {
	private Set<PageLayout> layouts;
	private List<String> keys;
	
	
	
	public SemiResponsiveConfigurationJava(Set<PageLayout> layouts) {
		this.layouts = layouts;
		this.keys = new ArrayList<String>();
		for (PageLayout layout : this.layouts) {
			keys.add(layout.getID());
		}
	}
	
	@Override
	public int length() {
		return this.layouts.size();
	}

	@Override
	public List<String> keys() {	
		return keys;
	}

	@Override
	public int getThreshold(String layoutID) {
		for (PageLayout layout : this.layouts) {
			if (layout.getID().equals(layoutID)) {
				return layout.getThreshold();
			}
		}
		
		return 0;
	}

	@Override
	public String getName(String layoutID) {
		for (PageLayout layout : this.layouts) {
			if (layout.getID().equals(layoutID)) {
				return layout.getName();
			}
		}
		
		return null;
	}

}
