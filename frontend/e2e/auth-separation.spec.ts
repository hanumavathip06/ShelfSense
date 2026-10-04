import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';

const ROLES = [
  {
    role: 'Admin',
    email: 'admin@test.com',
    password: 'password123',
    // Admin sees everything except items explicitly restricted via visibleToRoles
    allowedNav: [
      'Dashboard', 'Inventory', 'Stock Movements', 'Reports',
      'AI Forecast', 'Smart Reorder', 'Classification',
      'Users', 'System Settings', 'Audit Log', 'Stores & Locations'
    ],
    forbiddenRoutes: []
  },
  {
    role: 'Manager',
    email: 'manager@test.com',
    password: 'password123',
    // Manager sees main + ai, including manager-only items
    allowedNav: [
      'Dashboard', 'Inventory', 'Stock Movements', 'Reports',
      'Team', 'Bulk Import',
      'AI Forecast', 'Smart Reorder', 'Classification'
    ],
    forbiddenRoutes: ['/users', '/system-settings', '/audit-log', '/locations']
  },
  {
    role: 'Staff',
    email: 'staff@test.com',
    password: 'password123',
    // Staff sees only the 5 essentials
    allowedNav: [
      'Dashboard', 'Inventory', 'Stock Movements', 'Low Stock', 'Report Issue'
    ],
    forbiddenRoutes: [
      '/users', '/system-settings', '/audit-log', '/locations',
      '/reports', '/import', '/forecast', '/smart-reorder', '/classification', '/team'
    ]
  }
];

for (const { role, email, password, allowedNav, forbiddenRoutes } of ROLES) {
  test.describe(`Role Separation for ${role}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', password);
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/`);
    });

    test('should only see allowed sidebar navigation items', async ({ page }) => {
      for (const item of allowedNav) {
        const link = page.locator(`nav a:has-text("${item}")`);
        await expect(link).toBeVisible();
      }
    });

    test('should return 403 Forbidden when accessing unauthorized URLs directly', async ({ page }) => {
      for (const route of forbiddenRoutes) {
        await page.goto(`${BASE_URL}${route}`);
        await expect(page.locator('text=403 Forbidden')).toBeVisible();
      }
    });
  });
}
