import { TestBed, inject } from '@angular/core/testing';
import { HttpClientModule } from '@angular/common/http';
import { TransferHttpService } from '@gorniv/ngx-transfer-http';
import { TransferState } from '@angular/platform-browser';

import { MarkersService } from './markers.service';

describe('MarkersService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientModule],
            providers: [MarkersService, TransferHttpService, TransferState],
        });
    });

    it(
        'should be created',
        inject([MarkersService], (service: MarkersService) => {
            expect(service).toBeTruthy();
        })
    );
});
