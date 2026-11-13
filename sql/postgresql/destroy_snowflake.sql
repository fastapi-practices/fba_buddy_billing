delete from sys_menu
where name in (
    'AddFbaBuddyBillingPrice',
    'RechargeFbaBuddyBilling',
    'AdjustFbaBuddyBilling',
    'ReconcileFbaBuddyBilling',
    'AddFbaBuddyBillingBudget',
    'EditFbaBuddyBillingBudget',
    'DeleteFbaBuddyBillingBudget',
    'FbaBuddyBillingManage'
);

drop table if exists fba_buddy_billing_budget;
drop table if exists fba_buddy_billing_transaction;
drop table if exists fba_buddy_billing_ledger;
drop table if exists fba_buddy_billing_account;
drop table if exists fba_buddy_billing_price;
