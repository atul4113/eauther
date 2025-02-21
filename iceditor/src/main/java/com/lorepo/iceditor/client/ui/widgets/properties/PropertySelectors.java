package com.lorepo.iceditor.client.ui.widgets.properties;

import com.google.gwt.query.client.GQuery;
import com.google.gwt.query.client.Selector;
import com.google.gwt.query.client.Selectors;

public interface PropertySelectors extends Selectors {
	@Selector("propertyLabel")
	GQuery getLabel();
}
