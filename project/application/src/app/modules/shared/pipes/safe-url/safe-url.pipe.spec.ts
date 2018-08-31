import { Injector } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { getTestBed } from '@angular/core/testing';

import { SafeUrlPipe } from './safe-url.pipe';

describe('SafeUrlPipe', () => {
    let injector: Injector;

    it('create an instance', () => {
        injector = getTestBed();
        const pipe = new SafeUrlPipe(injector.get(DomSanitizer));
        expect(pipe).toBeTruthy();
    });
});
