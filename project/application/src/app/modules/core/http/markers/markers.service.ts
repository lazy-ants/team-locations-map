import { Injectable } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import { TransferHttpService } from '@gorniv/ngx-transfer-http';
import { Observable } from 'rxjs';

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

        return this.http.get(`${apiUrl}/markers`, { params });
    }
}
