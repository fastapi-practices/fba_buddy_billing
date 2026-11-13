do $$
declare
    ai_buddy_menu_id bigint;
    billing_menu_id bigint;
begin
    select id into ai_buddy_menu_id from sys_menu where name = 'PluginAIBuddy' and deleted = 0 order by id limit 1;

    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    select 'AI Buddy 计费', 'AIBuddyBillingManage', '/plugins/ai-buddy/billing', 14, 'material-symbols:payments-outline', 1, '/plugins/ai-buddy-billing/views/index', null, 1, 1, 1, '', null, ai_buddy_menu_id, now(), null
    where not exists (select 1 from sys_menu where name = 'AIBuddyBillingManage' and deleted = 0);
    select id into billing_menu_id from sys_menu where name = 'AIBuddyBillingManage' and deleted = 0 order by id limit 1;

    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    select v.title, v.name, null, v.sort, null, 2, null, v.perms, 1, 0, 1, '', null, billing_menu_id, now(), null
    from (values
        ('新增价格', 'AddAIBuddyBillingPrice', 0, 'ai:billing:price:add'),
        ('账户充值', 'RechargeAIBuddyBilling', 1, 'ai:billing:account:recharge'),
        ('余额调整', 'AdjustAIBuddyBilling', 2, 'ai:billing:account:adjust'),
        ('用量归集', 'ReconcileAIBuddyBilling', 3, 'ai:billing:reconcile'),
        ('新增预算', 'AddAIBuddyBillingBudget', 4, 'ai:billing:budget:add'),
        ('修改预算', 'EditAIBuddyBillingBudget', 5, 'ai:billing:budget:edit'),
        ('删除预算', 'DeleteAIBuddyBillingBudget', 6, 'ai:billing:budget:del'),
        ('查询计费账户', 'QueryAIBuddyBillingAccount', 7, 'ai:billing:account:list'),
        ('修改价格', 'EditAIBuddyBillingPrice', 8, 'ai:billing:price:edit'),
        ('删除价格', 'DeleteAIBuddyBillingPrice', 9, 'ai:billing:price:del')
    ) as v(title, name, sort, perms)
    where not exists (select 1 from sys_menu m where m.name = v.name and m.deleted = 0);
end $$;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
