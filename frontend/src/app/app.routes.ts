import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { adminGuard, auditGuard, orderGuard } from './guards/role.guard';
import { AuditComponent } from './pages/audit/audit.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { LayoutComponent } from './pages/layout/layout.component';
import { LoginComponent } from './pages/login/login.component';
import { OrdersComponent } from './pages/orders/orders.component';
import { InventoryComponent } from './pages/inventory/inventory.component';
import { ProductsComponent } from './pages/products/products.component';
import { UsersComponent } from './pages/users/users.component';
import { EventsComponent } from './pages/events/events.component';
import { RealtimeComponent } from './pages/realtime/realtime.component';
import { DlqComponent } from './pages/dlq/dlq.component';
import { ReadModelComponent } from './pages/readmodel/readmodel.component';
import { TenantsComponent } from './pages/tenants/tenants.component';
import { PlatformComponent } from './pages/platform/platform.component';
import { AiComponent } from './pages/ai/ai.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'tenants', component: TenantsComponent },
      { path: 'platform', component: PlatformComponent, canActivate: [adminGuard] },
      { path: 'products', component: ProductsComponent },
      { path: 'inventory', component: InventoryComponent },
      { path: 'orders', component: OrdersComponent, canActivate: [orderGuard] },
      { path: 'users', component: UsersComponent, canActivate: [adminGuard] },
      { path: 'audit', component: AuditComponent, canActivate: [auditGuard] },
      { path: 'events', component: EventsComponent, canActivate: [auditGuard] },
      { path: 'realtime', component: RealtimeComponent, canActivate: [auditGuard] },
      { path: 'dlq', component: DlqComponent, canActivate: [auditGuard] },
      { path: 'readmodel', component: ReadModelComponent, canActivate: [auditGuard] },
      { path: 'ai', component: AiComponent, canActivate: [auditGuard] },
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' }
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
