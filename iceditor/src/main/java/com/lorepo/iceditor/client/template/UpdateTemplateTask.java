package com.lorepo.iceditor.client.template;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.lorepo.icplayer.client.ContentDataLoader;
import com.lorepo.icplayer.client.model.Content;
import com.lorepo.icplayer.client.model.CssStyle;
import com.lorepo.icplayer.client.model.addon.AddonDescriptor;
import com.lorepo.icplayer.client.model.layout.PageLayout;

public class UpdateTemplateTask {
	/*
	 * Overrides Content Lesson Css Styles with Templates Styles when:
	 * 		- layout names are equal
	 * 		- layout have thresholds replaced too
	 * 		- template default layout overrides lesson default
	 * 
	 * Rest of layouts should be copied to lesson
	 */
	
	private class MatchingLayoutDTO {
		public boolean match;
		public String layoutID;
		
		public MatchingLayoutDTO(boolean match, String layoutID) {
			this.match = match;
			this.layoutID = layoutID;
		}
	}
	
	private ContentDataLoader addonLoader = new ContentDataLoader();
	
	public UpdateTemplateTask() {}
	
	public Content execute(Content theme, Content model) {
		this.updateSemiResponsiveTemplate(theme, model);
		this.addAddonsFromTemplate(model, theme.getAddonDescriptors().values());
		
		return model;
	}


	private void updateSemiResponsiveTemplate(Content themeContent, Content contentModel) {
		Set<PageLayout> themeLayouts = themeContent.getActualSemiResponsiveLayouts();
		HashMap<String, CssStyle> themeStyles = themeContent.getStyles();
		
		Set<PageLayout> contentLayouts = contentModel.getActualSemiResponsiveLayouts();
		HashMap<String, CssStyle> styles = contentModel.getStyles();
		
		
		this.overrideDefaultLayoutStyles(themeContent, contentModel);
		Set<PageLayout> layoutsToCopy = new HashSet<PageLayout>();
		for (PageLayout themeLayout: themeLayouts) {
			if (themeLayout.isDefault()) {
				continue;
			}
			
			MatchingLayoutDTO match = matchAnyLayout(themeLayout, contentLayouts);
			if (match.match) {
				CssStyle themeStyle = themeStyles.get(themeLayout.getStyleID());
				PageLayout matchingLayout = contentModel.getLayouts().get(match.layoutID);
				matchingLayout.setThreshold(themeLayout.getThreshold());
				CssStyle style = styles.get(matchingLayout.getStyleID());
				style.setValue(themeStyle.getValue());
			} else {
				layoutsToCopy.add(themeLayout);
			}
		}
		
		this.addMissingLayouts(layoutsToCopy, contentModel, themeStyles);
	}

	private void addMissingLayouts(Set<PageLayout> layoutsToCopy, Content contentModel, HashMap<String, CssStyle> themeStyles) {
		
		Set<Integer> thresholdsSet = new HashSet<Integer>();
		this.populateThresholds(thresholdsSet, contentModel.getLayouts());
		for (PageLayout themeLayout: layoutsToCopy) {
			int newThreshold = ensureDisjointThreshold(thresholdsSet, themeLayout.getThreshold(), contentModel.getLayouts());
			PageLayout newPageLayout = PageLayout.copy(themeLayout);
			newPageLayout.setThreshold(newThreshold);
			contentModel.addLayout(newPageLayout);
			contentModel.setStyle(CssStyle.copy(themeStyles.get(themeLayout.getID())));	
		}
	}

	private void populateThresholds(Set<Integer> thresholdsSet, HashMap<String, PageLayout> layouts) {
		for(PageLayout pl : layouts.values()) {
			thresholdsSet.add(pl.getThreshold());
		}
	}

	private int ensureDisjointThreshold(Set<Integer> thresholdsSet, int threshold, HashMap<String, PageLayout> layouts) {
		if (!thresholdsSet.contains(threshold)) {
			thresholdsSet.add(threshold);
			return threshold;
		} else {
			while(thresholdsSet.contains(threshold)) {
				threshold++;
			}
			
			thresholdsSet.add(threshold);
			return threshold;
		}
	}

	private void overrideDefaultLayoutStyles(Content themeContent, Content contentModel) {
		CssStyle themeDefaultStyle = themeContent.getDefaultCssStyle();
		CssStyle defaultStyle = contentModel.getDefaultCssStyle();
		defaultStyle.setValue(themeDefaultStyle.getValue());
		contentModel.setStyle(defaultStyle);
		
		String layoutID = contentModel.getDefaultSemiResponsiveLayoutID();
		String themeID = themeContent.getDefaultSemiResponsiveLayoutID();
		
		PageLayout defaultLayout = contentModel.getLayouts().get(layoutID);
		PageLayout themeDefaultLayout = themeContent.getLayouts().get(themeID);
		
		defaultLayout.setThreshold(themeDefaultLayout.getThreshold());
	}
	
	private MatchingLayoutDTO matchAnyLayout(PageLayout themeLayout, Set<PageLayout> contentLayouts) {
		for (PageLayout pl : contentLayouts) {
			if (themeLayout.getName().compareTo(pl.getName()) == 0) {
				return new MatchingLayoutDTO(true, pl.getID());
			}
		}
		
		return new MatchingLayoutDTO(false, "");
	}
	
	private void addAddonsFromTemplate(Content contentModel, Collection<AddonDescriptor> descriptors) {
		List<AddonDescriptor> newDescriptors = new ArrayList<AddonDescriptor>();
		
		for(AddonDescriptor desc : descriptors){
			if(!contentModel.getAddonDescriptors().containsKey(desc.getAddonId())){
				contentModel.getAddonDescriptors().put(desc.getAddonId(), desc);
				newDescriptors.add(desc);
			}
		}

		addonLoader.setBaseUrl(contentModel.getBaseUrl());
		addonLoader.addAddons(newDescriptors);
		addonLoader.load(null);
	}
}
