# AI Buddy Billing

为 AI Buddy 提供模型价格、用量账本、用户余额、充值调整、消费预算、账单归集和余额拦截

> 本插件是 AI Buddy 的可选扩展，通过 `depends_on` 在 AI Buddy 之后加载。不安装或停用本插件时，AI Buddy 的对话、工作和编码能力不受影响。

## 插件类型

- 应用级插件

## 配置说明

插件目录下 `plugin.toml` 的 `[settings]` 中包含以下内容：

```toml
[settings]
AI_BUDDY_BILLING_BALANCE_GUARD_ENABLED = true
AI_BUDDY_BILLING_BALANCE_MIN_USD = 0
AI_BUDDY_BILLING_BALANCE_GUARD_SKIP_SUPERUSER = false
```

当前项目的 `backend/core/conf.py` 已包含以下字段：

```python
##################################################
# [ Plugin ] ai_buddy_billing
##################################################
# 基础配置（in plugin.toml）
AI_BUDDY_BILLING_BALANCE_GUARD_ENABLED: bool = True
AI_BUDDY_BILLING_BALANCE_MIN_USD: Decimal = Decimal(0)
AI_BUDDY_BILLING_BALANCE_GUARD_SKIP_SUPERUSER: bool = False
```

## 配置项说明

- `AI_BUDDY_BILLING_BALANCE_GUARD_ENABLED`：是否在模型请求前校验计费余额，关闭后余额不足仍会继续运行
- `AI_BUDDY_BILLING_BALANCE_MIN_USD`：允许的最低余额，`0` 表示余额为非正数时阻断，配置负数可容许一定负债
- `AI_BUDDY_BILLING_BALANCE_GUARD_SKIP_SUPERUSER`：是否跳过超级管理员的余额校验

## 使用方式

1. 安装并启用 AI Buddy 插件和本插件后重启后端服务
   - 本插件在系统根级创建独立的“AI Buddy 计费”菜单（`/plugins/ai-buddy-billing`），与 AI Buddy 菜单平级，不挂在 AI Buddy 下
2. 按供应商和模型维护 token 单价、图片单价及生效时间，新价格会自动关闭上一版价格
3. 可修改价格单价或设置失效时间；未被账本使用的价格可以直接删除，已参与结算的价格只能失效
4. 通过账户列表查询用户余额，并按用户充值或调整余额
5. 按用户和运行、对话、日、月或总使用窗口配置 USD 与 token 上限
6. 由后台任务定时归集 AI Buddy 消息中的模型用量，也可以手动触发归集
7. 查询用户余额、计费流水、用量账本、消费预算和按时间范围汇总的费用

本插件记录的是 AI Buddy 用量结算账本，不接入支付渠道

用户存在计费账户且余额低于最低余额时，本轮模型请求会在发起前被阻断并返回 `billing_balance_insufficient` 错误码；没有计费账户的用户不受余额限制，按需先充值即可开户

消费预算使用 Harness SpendLimits 在模型请求前检查并在响应后累计，跨 worker 共享 Redis 计数器；并发请求可能在检查与记账之间小幅超过上限，精确结算以用量账本为准

## 卸载说明

- 卸载插件后清理 AI Buddy Billing 菜单、权限、消费预算和计费数据表
- 如业务已依赖余额、流水或账单数据，请先导出并完成结算
- 清理前端页面、定时归集任务和相关业务集成

## 联系方式

- 作者：`wu-clan`
- 反馈方式：提交 Issue 或 PR
