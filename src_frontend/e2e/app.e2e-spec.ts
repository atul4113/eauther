import { MauthorFrontendPage } from './app.po';

describe('mauthor-frontend App', () => {
  let page: MauthorFrontendPage;

  beforeEach(() => {
    page = new MauthorFrontendPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to app!!');
  });
});
