import { TestBed, async } from '@angular/core/testing';
import { TransferState } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { AgmCoreModule } from '@agm/core';
import { AgmJsMarkerClustererModule } from '@agm/js-marker-clusterer';
import { TransferHttpService } from '@gorniv/ngx-transfer-http';

import { HomeComponent } from './home.component';
import { CustomMaterialModule } from '../custom-material/custom-material.module';
import { SharedModule } from '../shared/shared.module';
import { AppSettingsConfig } from '../../configs/app-settings.config';
import { SeoPropertiesService } from '../core/services/seo-properties/seo-properties.service';
import { DocumentTitleService } from '../core/services/document-title/document-title.service';
import { TransferStateService } from '../core/services/transfer-state/transfer-state.service';
import { DocumentMetaService } from '../core/services/document-meta/document-meta.service';
import { DocumentLinkService } from '../core/services/document-link/document-link.service';
import { MarkersService } from '../core/http/markers/markers.service';

describe('HomeComponent', () => {
    beforeEach(
        async(() => {
            TestBed.configureTestingModule({
                imports: [
                    BrowserAnimationsModule,
                    HttpClientModule,
                    CustomMaterialModule,
                    AgmCoreModule.forRoot({
                        apiKey: AppSettingsConfig.google.apiKey,
                    }),
                    AgmJsMarkerClustererModule,
                    SharedModule,
                ],
                declarations: [HomeComponent],
                providers: [
                    {
                        provide: ActivatedRoute,
                        useValue: {
                            snapshot: {
                                data: {
                                    seoProps: {
                                        title: 'Lazy Ants - Team locations map',
                                    },
                                    seoPropsToRemove: {
                                        title: true,
                                    },
                                },
                            },
                        },
                    },
                    TransferHttpService,
                    TransferState,
                    TransferStateService,
                    SeoPropertiesService,
                    DocumentTitleService,
                    DocumentMetaService,
                    DocumentLinkService,
                    MarkersService,
                ],
            }).compileComponents();
        })
    );
    it(
        'should create the app',
        async(() => {
            const fixture = TestBed.createComponent(HomeComponent);
            const app = fixture.debugElement.componentInstance;
            expect(app).toBeTruthy();
        })
    );
    it(
        `should have lat as 50.471626, lng as 30.453608, zoom as 4.6`,
        async(() => {
            const fixture = TestBed.createComponent(HomeComponent);
            const app = fixture.debugElement.componentInstance;
            expect(app.lat).toEqual(50.471626);
            expect(app.lng).toEqual(30.453608);
            expect(app.zoom).toEqual(5);
        })
    );
});
