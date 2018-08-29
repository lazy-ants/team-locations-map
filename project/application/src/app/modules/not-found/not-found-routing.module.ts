import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { NotFoundComponent } from './not-found.component';

export const routes: Routes = [
    {
        path: '',
        component: NotFoundComponent,
        data: {
            seoProps: {
                title: 'Page not found',
            },
            seoPropsToRemove: {
                title: true,
            },
        },
    },
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
})
export class NotFoundRoutingModule {}
