delete from sys_menu
where name in (
    'AddAIBuddyBillingPrice',
    'RechargeAIBuddyBilling',
    'AdjustAIBuddyBilling',
    'ReconcileAIBuddyBilling',
    'AddAIBuddyBillingBudget',
    'EditAIBuddyBillingBudget',
    'DeleteAIBuddyBillingBudget',
    'QueryAIBuddyBillingAccount',
    'EditAIBuddyBillingPrice',
    'DeleteAIBuddyBillingPrice',
    'AIBuddyBillingManage'
);

drop table if exists ai_buddy_billing_budget;
drop table if exists ai_buddy_billing_transaction;
drop table if exists ai_buddy_billing_ledger;
drop table if exists ai_buddy_billing_account;
drop table if exists ai_buddy_billing_price;
