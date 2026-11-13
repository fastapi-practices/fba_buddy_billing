insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values (2147098509659216100, 'AI Buddy 计费', 'FbaBuddyBillingManage', '/plugins/ai-buddy/billing', 14, 'material-symbols:payments-outline', 1, '/plugins/fba-buddy-billing/views/index', null, 1, 1, 1, '', null, (select id from sys_menu where name = 'PluginAIBuddy'), now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2147098509659216101, '新增价格', 'AddFbaBuddyBillingPrice', null, 0, null, 2, null, 'ai:billing:price:add', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216102, '账户充值', 'RechargeFbaBuddyBilling', null, 1, null, 2, null, 'ai:billing:account:recharge', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216103, '余额调整', 'AdjustFbaBuddyBilling', null, 2, null, 2, null, 'ai:billing:account:adjust', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216104, '用量归集', 'ReconcileFbaBuddyBilling', null, 3, null, 2, null, 'ai:billing:reconcile', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216105, '新增预算', 'AddFbaBuddyBillingBudget', null, 4, null, 2, null, 'ai:billing:budget:add', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216106, '修改预算', 'EditFbaBuddyBillingBudget', null, 5, null, 2, null, 'ai:billing:budget:edit', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216107, '删除预算', 'DeleteFbaBuddyBillingBudget', null, 6, null, 2, null, 'ai:billing:budget:del', 1, 0, 1, '', null, 2147098509659216100, now(), null);
