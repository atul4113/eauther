package com.lorepo.iceditor.client.ui.widgets.docs;

import static com.google.gwt.query.client.GQuery.$;

import com.google.gwt.core.client.Callback;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Style.Display;
import com.google.gwt.query.client.GQuery;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.Widget;
import com.lorepo.iceditor.client.ui.widgets.content.MainPageEventListener;
import com.lorepo.iceditor.client.ui.widgets.content.WidgetLockerController;
import com.lorepo.icf.utils.i18n.DictionaryWrapper;
import com.lorepo.icplayer.client.model.addon.AddonDescriptorFactory;
import com.lorepo.icplayer.client.model.page.Page;
import com.lorepo.icplayer.client.module.addon.AddonModel;
import com.lorepo.icplayer.client.module.api.IModuleModel;
import com.lorepo.iceditor.client.ui.widgets.utils.MainPageUtils;

public class DocViewerWidget extends Composite {

	private static DocViewerWidgetUiBinder uiBinder = GWT
			.create(DocViewerWidgetUiBinder.class);

	interface DocViewerWidgetUiBinder extends
			UiBinder<Widget, DocViewerWidget> {
	}
	
	@UiField HTMLPanel panel;
	
	private boolean initialized = false;
	private AddonDescriptorFactory addonDescriptorsFactory = AddonDescriptorFactory.getInstance();
	
	public DocViewerWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		panel.getElement().setId("docViewerPage");
		hide();
		
		updateElementsTexts();
	}
	
	private void show(String name) {
		if (!initialized) {
			updateDocsScrollBarsOnResize(this);
			connectSectionNavs(this);
			initialized = true;
		}
		
		$("#docViewerPage-contents").find(".docViewerPage-docs").html("");
		$("#docViewerPage-contents").hide();
		$(panel.getElement()).find(".spinner-wrapper").show();
		MainPageUtils.showWithoutLockers(panel);
		
		setName(name);
	}
	
	public void show(IModuleModel module) {
		String moduleName = module.getProviderName();
		
		show(moduleName);
		loadDocs(module);
	}
	
	public void show (Page page) {
		String pageName = page.getProviderName();
		
		show(pageName);
		loadPageDocs(page);
	}
	
	public void hide() {
		WidgetLockerController.hide();
		panel.getElement().getStyle().setDisplay(Display.NONE);
	}
	
	public void setListener(final MainPageEventListener listener) {
		if (listener == null) {
			return;
		}
	}
	
	public void updateElementsTexts() {
		$(panel.getElement()).find(".spinner-wrapper").find(".spinner").find("span").text(DictionaryWrapper.get("documention_loading"));
	}
	
	private void setName(String name) {
		String docs = DictionaryWrapper.get("documentation");
		$(panel.getElement()).find(".mainPageHeader h3").text(docs + ": " + name);
	}
	
	private void showDocs (String html) {
		final GQuery spinner = $(panel.getElement()).find(".spinner-wrapper");
		final GQuery docsTargetParent = $("#docViewerPage-contents");
		final GQuery docsTarget = docsTargetParent.find(".docViewerPage-docs");
		
		spinner.hide();
		docsTargetParent.show();
		docsTarget.html(html);
		fixDocsSources();
		docsTargetParent.scrollTop(0);
		updateDocsScrollBars();
	}
	
	private void showDocs (DocumentationPage page) {
		showDocs(page.html);
	}
	
	private void showDocs (DocumentationSection section) {
		GQuery nav = $("<div>").addClass("docs-nav");
		GQuery pages = $("<div>").addClass("docs-pages");
		
		for (int i = 0; i < section.children.size(); i += 1) {
			DocumentationPage page = section.children.get(i);
			nav.append("<a data-page=\"" + i + "\">" + page.name + "</a>");
			pages.append("<div data-page=\"" + i + "\" class=\"docs-page\"><h2>" + page.name + "</h2>" + page.html + "</div>");
		}
		pages.find(".docs-page").hide();
		pages.find(".docs-page").first().show();
		nav.find("a").first().addClass("selected");
		
		showDocs(section.page.html + nav.toString() + pages.toString());
	}
	
	private void loadDocs(IModuleModel module) {
		boolean isPrivate = false;
		String moduleName = module.getModuleTypeName();
		
		if (module instanceof AddonModel) {
			isPrivate = !this.addonDescriptorsFactory.isLocalAddon(((AddonModel) module).getAddonId());
		}
		
		if (moduleName.equalsIgnoreCase("button")) {
			moduleName = module.getClassNamePrefix() + moduleName;
		}
		
		DocumentationService.getPage(moduleName, new Callback<DocumentationPage, String>() {

			@Override
			public void onFailure(String reason) {
				showDocs(DictionaryWrapper.get("documentation_error"));
			}

			@Override
			public void onSuccess(DocumentationPage page) {
				showDocs(page);
			}
		}, isPrivate);
	}
	
	private void loadPageDocs (Page page) {
		DocumentationService.getSection("Page", new Callback<DocumentationSection, String>() {

			@Override
			public void onFailure(String reason) {
				showDocs(DictionaryWrapper.get("documentation_error"));
			}

			@Override
			public void onSuccess(DocumentationSection section) {
				showDocs(section);
			}
		});
	}
	
	private native void updateDocsScrollBars () /*-{
		var docs = $wnd.document.getElementById("docViewerPage-contents");
		$wnd.Ps.update(docs); 
	}-*/;
	
	private native void updateDocsScrollBarsOnResize (DocViewerWidget x) /*-{
		$wnd.$("#docViewerPage").bind("resize", function () {
			x.@com.lorepo.iceditor.client.ui.widgets.docs.DocViewerWidget::updateDocsScrollBars()();
		}); 
	}-*/;
	
	private native void fixDocsSources () /*-{
		var docs = $wnd.$("#docViewerPage-contents").find(".docViewerPage-docs");
		
		docs.find("a").attr("target", "_blank");
		
		docs.find("img[src^='/file/serve/']").each(function() {
			var src = $wnd.$(this).attr("src");
			$wnd.$(this).attr("src", "https://www.mauthor.com" + src);
		});		
	}-*/;

	private native void connectSectionNavs (DocViewerWidget x) /*-{
		var $docsViewerContents = $wnd.$("#docViewerPage-contents");
		
		$docsViewerContents.on("click", ".docs-nav a", function (event) {
			var $this = $wnd.$(this), pageId = $this.attr("data-page"), docsPages;
			event.preventDefault();
			 
			$docsViewerContents.find(".docs-nav").children("a").removeClass("selected");
			$this.addClass("selected");
			
		 	docsPages = $docsViewerContents.find(".docs-pages");
		 	docsPages.children().hide();
		 	docsPages.find(".docs-page[data-page=\"" + pageId + "\"]").show();
		 	
		 	$docsViewerContents.scrollTop(0);
		 	x.@com.lorepo.iceditor.client.ui.widgets.docs.DocViewerWidget::updateDocsScrollBars()();
		});
	}-*/;
}
