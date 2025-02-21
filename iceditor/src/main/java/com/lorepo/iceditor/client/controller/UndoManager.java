package com.lorepo.iceditor.client.controller;

import java.util.ArrayList;
import java.util.List;

import com.lorepo.icplayer.client.model.page.Page;

public class UndoManager implements IUndoManager {
	class State{
		String name;
		String value;
		State(String n, String v){ name = n; value = v; }
	}
	
	private UndoManagerEventListener listener;
	private List<State> states = new ArrayList<State>();
	private int index = 0;
	
	public UndoManager (Page page, UndoManagerEventListener listener) {
		this.listener = listener;
		add("init", page.toXML());
	}
	
	@Override
	public void add(String value) {
		addState("", value);
	}

	@Override
	public void add(String name, String value) {
		addState(name, value);
	}
	
	private void addState(String name, String value){
		while(states.size() > index+1){
			states.remove(states.size()-1);
		}
		states.add(new State(name, value));
		index = states.size()-1;
	}

	@Override
	public void clear() {
		states.clear();
		
	}

	@Override
	public void undo() {
		if (index > 0 && index < states.size()) {
			index -= 1;
			
			if (listener != null) {
				listener.onPageXMLChanged(states.get(index).value);
			}
		}
	}

	@Override
	public void redo() {
		if (index < states.size() - 1) {
			index += 1;
			
			if (listener != null) {
				listener.onPageXMLChanged(states.get(index).value);
			}
		}
	}
}
