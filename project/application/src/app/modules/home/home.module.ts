import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgmCoreModule } from '@agm/core';
import { AgmJsMarkerClustererModule } from '@agm/js-marker-clusterer';

import { HomeRoutingModule } from './home-routing.module';
import { CustomMaterialModule } from '../custom-material/custom-material.module';
import { SharedModule } from '../shared/shared.module';
import { AppSettingsConfig } from '../../configs/app-settings.config';
import { HomeComponent } from './home.component';

@NgModule({
    imports: [
        HomeRoutingModule,
        CommonModule,
        CustomMaterialModule,
        AgmCoreModule.forRoot({
            apiKey: AppSettingsConfig.google.apiKey,
        }),
        AgmJsMarkerClustererModule,
        SharedModule,
    ],
    declarations: [HomeComponent],
})
export class HomeModule {}
