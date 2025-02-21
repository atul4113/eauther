package com.lorepo.iceditor.client.utils.ui.styleeditor;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import com.google.gwt.regexp.shared.MatchResult;
import com.google.gwt.regexp.shared.RegExp;

public class CssParser {

	public CssParser(){
	}
	
	private String[] extractClasses(String classes) {
		int position = 0;
		String[] multiClass;
		
		classes = classes.replaceAll("[\\s.{]", "");

		if (classes.contains("*/")) {
			position = classes.indexOf("*/") + 2;
			classes = classes.substring(position);
		}
		
		multiClass = classes.split(",");

		return multiClass;
	}
	
	/* First regular expression match css lines with possible comment on begin such as:
	 * .Addon_Class1 { ...
	 * 
	 * Second regular expression match css lines with possible comment on begin such as:
	 * .Addon_Class1, .Addon_Class2, .Addon_Class3 { ...
	 */ 
	
	public List<String> findClasses(String css) {
		ArrayList<String> classNames = new ArrayList<String>();
		if (css == "" || css == null) {
			return classNames;
		}
		
		String pattern = "^(\\s*(.*)\\s*\\*/)?\\s*\\.(-?[_a-zA-Z]+[_a-zA-Z0-9-]+\\s*\\{)";
		String patternMulti = "^(\\s*(.*)\\s*\\*/)?\\s*\\.-?[_a-zA-Z0-9-]+[_a-zA-Z0-9-]+(,\\s*.-?[_a-zA-Z0-9-]+[_a-zA-Z0-9-])+\\s*\\{";
		String cssLines[] = css.split("\\r?\\n");
		RegExp regExpPattern = RegExp.compile(pattern, "g");
		RegExp regExpPatternMulti = RegExp.compile(patternMulti, "g");
		MatchResult matcher, matcherMulti;
		boolean matchFound, matchMultiClassesFound;
		String multiClasses[];
		
		for(int i = 0; i < cssLines.length; i++) {
			
			matcher = regExpPattern.exec(cssLines[i]);
			matcherMulti = regExpPatternMulti.exec(cssLines[i]);
			matchFound = matcher != null;
			matchMultiClassesFound = matcherMulti != null;
			
			if (matchFound) {				
			    for (int j = 1; j < matcher.getGroupCount(); j++) {
			    	if (matcher.getGroup(j) != null) {
			    		String text = matcher.getGroup(j).replaceAll("[\\s{]","");
						int pos = text.indexOf("/");

						if (pos == -1) {
							classNames.add(text);
						}
					}
			    }
			} else if (matchMultiClassesFound) {

				multiClasses = extractClasses(matcherMulti.getGroup(0));

				for (int j = 0; j < multiClasses.length; j++) {
					classNames.add(multiClasses[j]);
				}
			}
		}
		
		Set<String> classNamesSet = new LinkedHashSet<String>(classNames);
		classNames.clear();
		classNames.addAll(classNamesSet);

		return classNames;
	}
}
