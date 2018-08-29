import { NotFoundPage } from './not-found.po';

describe('workspace-project NotFound', () => {
    let page: NotFoundPage;

    beforeEach(() => {
        page = new NotFoundPage();
    });

    it('should display not found message', () => {
        page.navigateTo();
        expect(page.getParagraphText()).toEqual('Page not found');
    });
});
