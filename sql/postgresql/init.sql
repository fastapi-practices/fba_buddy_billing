do $$
declare
    ai_buddy_menu_id bigint;
    billing_menu_id bigint;
begin
    select id into ai_buddy_menu_id from sys_menu where name = 'PluginAIBuddy';

    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    values ('AI Buddy 计费', 'FbaBuddyBillingManage', '/plugins/ai-buddy/billing', 14, 'material-symbols:payments-outline', 1, '/plugins/fba-buddy-billing/views/index', null, 1, 1, 1, '', null, ai_buddy_menu_id, now(), null)
    returning id into billing_menu_id;

    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    values
    ('新增价格', 'AddFbaBuddyBillingPrice', null, 0, null, 2, null, 'ai:billing:price:add', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('账户充值', 'RechargeFbaBuddyBilling', null, 1, null, 2, null, 'ai:billing:account:recharge', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('余额调整', 'AdjustFbaBuddyBilling', null, 2, null, 2, null, 'ai:billing:account:adjust', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('用量归集', 'ReconcileFbaBuddyBilling', null, 3, null, 2, null, 'ai:billing:reconcile', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('新增预算', 'AddFbaBuddyBillingBudget', null, 4, null, 2, null, 'ai:billing:budget:add', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('修改预算', 'EditFbaBuddyBillingBudget', null, 5, null, 2, null, 'ai:billing:budget:edit', 1, 0, 1, '', null, billing_menu_id, now(), null),
    ('删除预算', 'DeleteFbaBuddyBillingBudget', null, 6, null, 2, null, 'ai:billing:budget:del', 1, 0, 1, '', null, billing_menu_id, now(), null);
end $$;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
