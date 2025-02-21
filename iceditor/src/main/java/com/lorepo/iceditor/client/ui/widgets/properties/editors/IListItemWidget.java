package com.lorepo.iceditor.client.ui.widgets.properties.editors;

import com.lorepo.icf.properties.IProperty;

public interface IListItemWidget {
	public void setName(String name);
	public void setProperty(IProperty property);
	public void save();
	public void reset();
	public boolean isModified();
}
