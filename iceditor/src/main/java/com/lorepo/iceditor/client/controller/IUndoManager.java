package com.lorepo.iceditor.client.controller;

public interface IUndoManager {
	public void add(String value);
	public void add(String name, String value);
	public void clear();
	
	public void undo();
	public void redo();
	
	public interface UndoManagerEventListener {
		public void onPageXMLChanged(String xml);
	}
}
