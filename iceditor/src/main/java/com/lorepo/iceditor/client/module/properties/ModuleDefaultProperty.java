package com.lorepo.iceditor.client.module.properties;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class ModuleDefaultProperty {
	private static List<String> protectedIntegerProperties = Arrays.asList(new String[] {"Left", "Top", "Width", "Height", "Right", "Bottom"});
	private static List<String> forbiddenProperties = Arrays.asList(new String[] {"ID", "Layout", "Is Visible"});
	
	
	public String name;
	public String value;
	public List<Map<String, ModuleDefaultProperty>> listValue;
	
	public ModuleDefaultProperty () {}
	
	public ModuleDefaultProperty (String name) {
		this.name = name;
		this.value = null;
		this.listValue = null;
	}
	
	public ModuleDefaultProperty (String name, String value) {
		this(name);
		this.value = value;
	}
	
	public ModuleDefaultProperty (String name, List<Map<String, ModuleDefaultProperty>> complexValue) {
		this(name);
		this.listValue = complexValue;
	}
	
	public boolean isList () {
		return this.value == null && this.listValue != null;
	}
	
	public boolean isSimple () {
		return this.value != null && this.listValue == null;
	}
	
	public boolean isEmpty () {
		return this.value == null && this.listValue == null;
	}
	
	public String toString () {
		return "{ModuleDefaultProperty:: " +
				(isList() ? this.listValue.toString() : this.value)
				+ "}";
	}
	
	public boolean isForbidden () {
		for(String name : forbiddenProperties) {
			if (name.compareToIgnoreCase(this.name) == 0) {
				return true;
			}
		}
		return false;
	}
	
	public boolean isProtectedInteger () {
		for(String name : protectedIntegerProperties) {
			if (name.compareToIgnoreCase(this.name) == 0) {
				return true;
			}
		}
		return false;
	}
}
