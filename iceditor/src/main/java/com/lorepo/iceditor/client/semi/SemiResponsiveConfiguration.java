package com.lorepo.iceditor.client.semi;

import java.util.List;

public interface SemiResponsiveConfiguration {
	public int length();
	public List<String> keys();
	public int getThreshold(String layoutID);
	public String getName(String layoutID);
}
