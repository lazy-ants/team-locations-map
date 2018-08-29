import { browser, by, element } from 'protractor';

export class NotFoundPage {
    navigateTo() {
        return browser.get('/404');
    }

    getParagraphText() {
        return element(by.css('app-root h1')).getText();
    }
}
