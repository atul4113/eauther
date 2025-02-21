package com.lorepo.iceditor.client.semi;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

import com.lorepo.icplayer.client.model.layout.PageLayout;

public class SemiResponsiveConfigurationMock implements SemiResponsiveConfiguration {
	
	HashMap<String, PageLayout> configuration = new HashMap<String, PageLayout>();
	
	public SemiResponsiveConfigurationMock(HashMap<String, PageLayout> configuration) {
		this.configuration = configuration;
	}
	
	@Override
	public int length() {
		return this.configuration.size();
	}
	
	@Override
	public List<String> keys() {
		List<String> result = new LinkedList<String>();
		for(String key : this.configuration.keySet()) {
			result.add(key);
		}
		
		return result;
	}
	
	@Override
	public int getThreshold(String layoutID) {
		return this.configuration.get(layoutID).getThreshold();
	}
	
	@Override
	public String getName(String layoutID) {
		return this.configuration.get(layoutID).getName();
	}

}
