insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
select v.id, v.title, v.name, v.path, v.sort, v.icon, v.type, v.component, v.perms, v.status, v.display, v.cache, v.link, v.remark, v.parent_id, v.created_time::timestamptz, v.updated_time::timestamptz
from (values
(2147098509659216100, 'AI Buddy 计费', 'AIBuddyBillingManage', '/plugins/ai-buddy/billing', 14, 'material-symbols:payments-outline', 1, '/plugins/ai-buddy-billing/views/index', null, 1, 1, 1, '', null, (select id from sys_menu where name = 'PluginAIBuddy' and deleted = 0 order by id limit 1), now(), null),
(2147098509659216101, '新增价格', 'AddAIBuddyBillingPrice', null, 0, null, 2, null, 'ai:billing:price:add', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216102, '账户充值', 'RechargeAIBuddyBilling', null, 1, null, 2, null, 'ai:billing:account:recharge', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216103, '余额调整', 'AdjustAIBuddyBilling', null, 2, null, 2, null, 'ai:billing:account:adjust', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216104, '用量归集', 'ReconcileAIBuddyBilling', null, 3, null, 2, null, 'ai:billing:reconcile', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216105, '新增预算', 'AddAIBuddyBillingBudget', null, 4, null, 2, null, 'ai:billing:budget:add', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216106, '修改预算', 'EditAIBuddyBillingBudget', null, 5, null, 2, null, 'ai:billing:budget:edit', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216107, '删除预算', 'DeleteAIBuddyBillingBudget', null, 6, null, 2, null, 'ai:billing:budget:del', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216108, '查询计费账户', 'QueryAIBuddyBillingAccount', null, 7, null, 2, null, 'ai:billing:account:list', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216109, '修改价格', 'EditAIBuddyBillingPrice', null, 8, null, 2, null, 'ai:billing:price:edit', 1, 0, 1, '', null, 2147098509659216100, now(), null),
(2147098509659216110, '删除价格', 'DeleteAIBuddyBillingPrice', null, 9, null, 2, null, 'ai:billing:price:del', 1, 0, 1, '', null, 2147098509659216100, now(), null)
) as v(id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
where not exists (select 1 from sys_menu m where m.id = v.id or (m.name = v.name and m.deleted = 0));
