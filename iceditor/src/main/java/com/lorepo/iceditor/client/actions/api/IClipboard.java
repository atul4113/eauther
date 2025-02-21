package com.lorepo.iceditor.client.actions.api;

import java.util.ArrayList;
import java.util.Iterator;

public interface IClipboard {

	public void setData(ArrayList<String> data);
	public Iterator<String> getData();
}
