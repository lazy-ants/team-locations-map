import { NgModule } from '@angular/core';
import { BrowserModule, BrowserTransferStateModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { RoutingModule } from '../routing/routing.module';

@NgModule({
    imports: [
        BrowserModule.withServerTransition({ appId: 'angular-universal' }),
        BrowserTransferStateModule,
        BrowserAnimationsModule,
        RoutingModule,
    ],
})
export class CoreModule {}
