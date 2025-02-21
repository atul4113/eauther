package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.Iterator;

import com.lorepo.iceditor.client.actions.api.IClipboard;

public class Clipboard implements IClipboard {

	private ArrayList<String>	data = new ArrayList<String>();
	
	
	public void setData(ArrayList<String> data){
	
		this.data = data;
	}
	
	public Iterator<String> getData(){
		return data.iterator();
	}
}
