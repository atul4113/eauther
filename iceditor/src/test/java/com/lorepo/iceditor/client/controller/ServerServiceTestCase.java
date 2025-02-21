package com.lorepo.iceditor.client.controller;

import static org.junit.Assert.assertEquals;
import java.io.IOException;
import org.junit.Test;
import com.lorepo.iceditor.client.actions.mockup.AppControllerMockup;

public class ServerServiceTestCase {

	@Test
	public void createURL() throws IOException {
		AppControllerMockup appController = new AppControllerMockup(null);
		appController.loadContent("/file/001");
		ServerService service = new ServerService();
		service.setAppController(appController);

		String url = service.createURL("123");

		assertEquals("/editor/api/addNewPage?content_file=/file/001&page=123", url);
	}
	
}
