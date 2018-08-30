import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID, ViewChild } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

import { SeoPropertiesService } from '../core/services/seo-properties/seo-properties.service';
import { Marker, MarkersService as MarkersHttpService } from '../core/http/markers/markers.service';
import * as googleMapStyles from '../core/mocks/google-map-styles/google-map-styles.json';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
})
export class HomeComponent implements OnInit, OnDestroy {
    // initial center position for the map
    lat = 50.471626;
    lng = 30.453608;
    zoom = 5;
    styles: any = googleMapStyles.default;
    markers: Marker[] = [];
    markerInfo: Marker;
    @ViewChild('drawer') sidenav;

    constructor(
        private route: ActivatedRoute,
        private seoPropertiesService: SeoPropertiesService,
        private markersHttpService: MarkersHttpService,
        @Inject(PLATFORM_ID) private platformId: Object
    ) {}

    ngOnInit() {
        this.seoPropertiesService.setSeoProps(this.route.snapshot.data.seoProps);
        this.markersHttpService.getMarkers().subscribe((response: any) => (this.markers = response._items));
    }

    ngOnDestroy() {
        if (isPlatformBrowser(this.platformId)) {
            // Be attention! This statement is required by the Angular Universal's bug
            // I found today. The ngOnDestroy() hook calls every time on the server side
            // when the browser page refreshes.
            this.seoPropertiesService.removeSeoProps(this.route.snapshot.data.seoPropsToRemove);
        }
    }

    public setMarkerInfo(marker: Marker): void {
        if (!!marker) {
            this.markerInfo = marker;
            this.sidenav.open();
        }
    }
}
