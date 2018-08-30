import { Injectable } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { TransferHttpService } from '@gorniv/ngx-transfer-http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import * as _ from 'underscore';

import { CoreModule } from '../../core.module';
import { AppSettingsConfig } from '../../../../configs/app-settings.config';

interface MarkerLocation {
    name: string;
    lat: number;
    lng: number;
}

export interface Marker {
    location: MarkerLocation;
    username: string;
    workPosition?: string;
    email?: string;
    skype?: string;
    bio?: string;
    avatar: string;
}

@Injectable({
    providedIn: CoreModule,
})
export class MarkersService {
    private appSettingsConfig = AppSettingsConfig;
    private googleCoordinatesAccuracy = 7; // decimal places in google coordinate values **.YYYYYYY

    constructor(private http: TransferHttpService) {}

    public getMarkers(): Observable<any> {
        const apiUrl = this.appSettingsConfig.api.url;
        const params = new HttpParams().set('max_results', '50').set(
            'projection',
            JSON.stringify({
                location: 1,
                username: 1,
                workPosition: 1,
                email: 1,
                skype: 1,
                bio: 1,
                avatar: 1,
            })
        );

        return this.http.get(`${apiUrl}/markers`, { params }).pipe(
            map((data: any) => {
                data._items = this.correctGroupedMarkers(data._items);

                return data;
            })
        );
    }

    private correctGroupedMarkers(markers: Marker[]): Marker[] {
        const markersGrouped = _.groupBy(markers, (marker: Marker) => `${marker.location.lat},${marker.location.lng}`);

        const markersCorrected = [];
        const markersGroupedKeys = _.keys(markersGrouped);
        markersGroupedKeys.map(key => {
            markersGrouped[key].map((marker: Marker, index: number) => {
                const indexCorrected = index + 1;
                const round = Math.ceil(indexCorrected / 4);
                const roundPrev = round - 1;

                // the main purpose to get the next sign sequence
                // 1 1
                // -1 1
                // 1 -1
                // -1 -1
                const latSign = indexCorrected - roundPrev * 4 > 2 ? -1 : 1;
                const lngSign = (indexCorrected - roundPrev * 4) % 2 === 1 ? 1 : -1;

                // don't know, but these values make the markers evenly distributed
                const latCorrectValue = 55;
                const lngCorrectValue = 80;

                marker.location.lat += latSign * latCorrectValue * (round / 10 ** this.googleCoordinatesAccuracy);
                marker.location.lng += lngSign * lngCorrectValue * (round / 10 ** this.googleCoordinatesAccuracy);
                markersCorrected.push(marker);
            });
        });

        return markersCorrected;
    }
}
