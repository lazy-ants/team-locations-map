import { NgModule } from '@angular/core';
import { BrowserModule, BrowserTransferStateModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { TransferHttpModule } from '@gorniv/ngx-transfer-http';

import { RoutingModule } from '../routing/routing.module';

@NgModule({
    imports: [
        BrowserModule.withServerTransition({ appId: 'angular-universal' }),
        BrowserTransferStateModule,
        BrowserAnimationsModule,
        HttpClientModule,
        TransferHttpModule,
        RoutingModule,
    ],
})
export class CoreModule {}
