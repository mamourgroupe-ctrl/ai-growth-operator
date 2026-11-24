# تقرير معالجة ملاحظات قبول المرحلة الأولى

التاريخ: 2026-11-24 (UTC)  
المستودع: `mamourgroupe-ctrl/ai-growth-operator`  
الفرع: `arena/5dc98770-ai-growth-operator`  
HEAD بعد الإصلاحات: `9ec073f9ca9adb2c60100553ba26cbfd114f7034`  
الوثيقة المرجعية: `docs/phase-1/independent-acceptance-audit.md`

هذا التقرير يغطي نقاط `FAIL` و`PARTIAL` ذات الصلة بقبول Phase 1 فقط. لم يُبدأ Phase 2، ولم يُجرَ نشر إنتاجي أو إنفاق مالي، ولم يُدمج PR #15، ولم يُعدّل `main`.

## 0. ملخص Commit/Issue

| Issue | المشكلة | Commit | ملاحظة |
|---|---|---|---|
| — | حفظ تقرير التدقيق المستقل | `189b731` | docs-only، لا يغيّر السلوك |
| #28 | دور التطبيق و RLS عبر API | `7d42952` | إصلاح + اختبارات |
| #30 | FK لسجل التدقيق | `f5f963e` | هجرة + نموذج + اختبار |
| #29 | عكسية Alembic | `8424ae3` | إصلاح downgrade + اختبار دورة كاملة |
| #31 | انتهاء/إبطال الجلسة | `5e45feb` | اختبارات آلية |
| #32 | فاحص الأسرار | `155fea6` | توسيع + توثيق + اختبارات |
| #14 | حماية فرع `main` | `9ec073f` | توثيق فقط؛ Issue ما زال مفتوحاً |

ترتيب الـ commits مختلف عن ترتيب أرقام Issues لأن هجرة FK أُضيفت قبل اختبار الدورة الكاملة حتى يشمل اختبار reversibility أحدث revision.

---

## 1. دور قاعدة البيانات في وقت التشغيل و RLS — Issue #28

### المشكلة الأصلية

التدقيق وجد أن `AGO_DATABASE_URL` كان يُستخدم من قِبل FastAPI، وفي الاختبارات كان يشير إلى حساب	superuser، بينما `AGO_APP_DATABASE_URL` كان مُعرّفاً لكنه غير مستخدم. لذلك كانت اختبارات API تعمل بدور ممتاز، ولم يكن RLS مُطبّقاً فعلياً على مسارات API في CI.

### الملفات المعدّلة

- `apps/api/app/config.py` — توثيق صريح: `database_url` للهجرات فقط، و`app_database_url` لتشغيل API.
- `apps/api/app/db.py` — `get_engine()` يقرأ الآن `app_database_url`.
- `.env.example` — توضيح أن `AGO_DATABASE_URL` للهجرات، و`AGO_APP_DATABASE_URL` يجب أن يكون rol غير ممتاز `NOBYPASSRLS`، وإضافة `AGO_APP_ROLE`.
- `tests/test_app_role_runtime.py` — اختبارات جديدة.

### Commit

`7d42952 fix(#28): run API with non-privileged app role and test RLS via API`

### الاختبارات التي تثبت الحل

- `test_runtime_engine_uses_app_database_url` — يتحقق أن محرك API يستخدم `database.app_url` وليس admin URL.
- `test_app_role_is_not_privileged` — يقرأ `pg_roles` ويؤكد `rolsuper=false`, `rolbypassrls=false`, `rolcanlogin=true`.
- `test_api_runs_through_app_role_and_rejects_cross_tenant_access` — مستخدمان حقيقيان عبر `TestClient`؛ B يحصل على `404` عند قراءة مؤسسة A، وA يضيف B كـ editor بنجاح، ثم B يُمنع `403` من تعديل مؤسسة A لأنه ليس owner.
- `test_tenant_context_is_transaction_local_and_pool_safe` — يضبط السياق عبر `set_tenant_context()` داخل معاملة، ثم يعيد الاتصال نفسه من `pool_size=1` ويؤكد أن `app.current_tenant_id` و`app.current_user_id` عائdan إلى `''`.

### الأوامر والنتائج الفعلية

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider tests/test_app_role_runtime.py
....                                                                     [100%]
```

فحص يدوي إضافي قبل الإصلاح وبعده أكد أن `GET /organizations/{org_a}` من المستخدم B يُرجع `404` و`GET /organizations/{org_a}` من A يُرجع `200` عند تشغيل API بدور `ago_app`.

### ما بقي دون حل

لا شيء ضمن نطاق هذه المشكلة. جداول `users` و`sessions` تبقى جداول هوية عامة بدون RLS حسب التصميم الحالي، ويُعتمد على فلاتر التطبيق للوصول إليها؛ هذا مذكور كحد تصميمي وليس كفشل جديد.

---

## 2. عكسية Alembic — Issue #29

### المشكلة الأصلية

`alembic downgrade base` كان يفشل:

```text
psycopg.errors.DependentObjectsStillExist: cannot drop table tenant_memberships because other objects depend on it
DETAIL: policy tenant_isolation on table tenants depends on table tenant_memberships
```

### الملفات المعدّلة

- `apps/api/migrations/versions/0001_initial.py` — أُضيف `_drop_rls()` وتم استدعاؤه قبل إسقاط الجداول؛ يحذف `tenant_isolation` ثم يعطل `FORCE` و`RLS` على الجداول الخمسة.
- `tests/test_migration_reversibility.py` — اختبار دورة كاملة على PostgreSQL فارغ عبر `pgserver`.

### Commit

`8424ae3 fix(#29): make Alembic downgrade reversible and test full cycle`

### الاختبار الذي يثبت الحل

`test_upgrade_downgrade_upgrade_preserves_schema`:

1. ينشئ Postgres مؤقتاً ودور `ago_app` غير ممتاز.
2. `upgrade head` → يتحقق أنRevision هو `0002_audit_log_tenant_fk`.
3. يأخذ snapshot للجداول والفهارس والقيود والسياسات وأعلام RLS.
4. `downgrade base` → يتحقق أن جداول النطاق كلها اختفت وأن `alembic_version` فارغ.
5. `upgrade head` again → يقارن الـ snapshot الجديد بالأول ويؤكد تطابقهما.

### الأوامر والنتائج الفعلية

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider tests/test_migration_reversibility.py
.                                                                        [100%]
```

### ما بقي دون حل

لا شيء ضمن نطاق هذه المشكلة. البيانات نفسها لا تُحتفظ بعد `downgrade base` لأن الجداول تُسقط؛ المطلوب كان سلامة المخطط بعد إعادة الترقية، وقد تحققت.

---

## 3. سلامة سجل التدقيق — Issue #30

### المشكلة الأصلية

`audit_logs.tenant_id` كان قابلاً للـ NULL وبلا FK، بعكس بقية جداول المستأجرين.

### القرار التصميمي

أُضيف FK إلى `tenants.id` بـ `ON DELETE RESTRICT` وليس `CASCADE`، لأن سجلات التدقيق تُحفظ لأغراض الاحتفاظ. الجداول الأخرى تستخدم `CASCADE`، لكن حذف tenant نهائياً مع وجود سجلات تدقيق يجب أن يُرفض حتى تُعالج سياسة الاحتفاظ صراحةً. الحذف الطبيعي في Phase 1 هو حذف ناعم عبر `deleted_at`، لذلك لا يتأثر.

### الملفات المعدّلة

- `apps/api/migrations/versions/0002_audit_log_tenant_fk.py` — هجرة جديدة بـ `upgrade()` و`downgrade()`.
- `apps/api/app/models.py` — `ForeignKey("tenants.id", ondelete="RESTRICT")` على `AuditLog.tenant_id`.
- `tests/test_audit_log_integrity.py` — اختبار القيد.

### Commit

`f5f963e fix(#30): add retention-safe audit_logs tenant FK and tests`

### الاختبار الذي يثبت الحل

`test_audit_log_tenant_fk_blocks_unknown_tenant_and_hard_delete`:

- يزرع tenant ومستخدم بعضوية owner عبر دور التطبيق.
- يكتب سجل تدقيق بـ tenant صالح عبر API role.
- يؤكد وجود القيد `fk_audit_logs_tenant_id` في `pg_constraint`.
- يحاول إدراج سجل تدقيق بـ tenant غير موجود عبر حساب إداري → `IntegrityError`.
- يحاول حذف الـ tenant مباشرة → `IntegrityError` بسبب `RESTRICT`.
- يحذف سجل التدقيق ثم الـ tenant بنجاح، لإثبات أن القيد لا يمنع الحذف بعد إزالة السبب.

### الأوامر والنتائج الفعلية

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider tests/test_audit_log_integrity.py
.                                                                        [100%]
```

### ما بقي دون حل

`tenant_id` لا يزال nullable للسماح بسجلات نظام غير مرتبطة بمستأجر؛ مثل هذه السجلات لا تظهر لمستخدمي المستأجرين بسبب `RLS WITH CHECK/USING`. كان تركيز المعالجة على سلامة الربط عند وجود tenant.

---

## 4. انتهاء الجلسة وإبطالها — Issue #31

### المشكلة الأصلية

انتهاء الجلسة كان مُختبَر يدوياً فقط أثناء التدقيق، ولم تكن هناك اختبارات آلية لـ idle expiry أو absolute expiry أو الإبطال المباشر.

### الملفات المعدّلة

- `tests/test_session_expiry.py` — ملف اختبارات جديد فقط؛ لم يتغير سلوك المصادقة.

### Commit

`5e45feb test(#31): automate session expiry and revocation checks`

### الاختبارات التي تثبت الحل

- `test_idle_expiry_rejects_authenticated_routes` — يضع `expires_at` في الماضي عبر اتصال إداري ثم يتوقع `401` على `/auth/me` و`/organizations`.
- `test_absolute_expiry_rejects_session` — يضع `absolute_expires_at` في الماضي ثم يتوقع `401`.
- `test_direct_revocation_rejects_session` — يضع `revoked_at` ثم يتوقع `401`.
- `test_logout_marks_session_revoked` — يتحقق أن `POST /auth/logout` يضبط `revoked_at` في قاعدة البيانات ثم يرفض الجلسة.

### الأوامر والنتائج الفعلية

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider tests/test_session_expiry.py
....                                                                     [100%]
```

### ما بقي دون حل

لا توجد نقطة نهاية لإبطال كل جلسات المستخدم أو تدوير الرموز؛ لم تُضف لأنها ميزة جديدة خارج نطاق Phase 1 Remediation.

---

## 5. فاحص الأسرار — Issue #32

### المشكلة الأصلية

الفاحص كان يفحص مجلدَي `apps/api/app` و`apps/web/app` فقط، بنمط ضيّق، ويطبع السطر المطابق كاملاً — وهو خطر إذا كان السطر يحتوي سراً حقيقياً. لم تكن الاستثناءات موثقة.

### الملفات المعدّلة

- `scripts/check_no_secrets.py` — إعادة كتابة: فحص كل المستودع، خمس قواعد، استثناءات صريحة، عدم طباعة القيم، دعم جذر بديل للاختبارات.
- `docs/phase-1/secret-scanner.md` — جدول القواعد وجدول كل استثناء وسببه وترتيب القواعد.
- `tests/test_secret_scanner.py` — اختبارات الفاحص نفسه.
- `tests/test_auth.py`, `tests/test_rbac.py`, `tests/test_tenant_isolation.py` — إضافة وسم `secret-scan-exempt: dummy test credential` لكلمات المرور الوهمية فقط.
- وسم مماثل كان موجوداً بالفعل في `tests/test_app_role_runtime.py` و`tests/test_session_expiry.py`.

### Commit

`155fea6 fix(#32): broaden secret scan, document exceptions, add scanner tests`

### الاختبارات التي تثبت الحل

- `test_detects_quoted_secret_without_printing_value` — يؤكد اكتشاف الإسناد الحساس، وأن القيمة لا تظهر في `Finding` ولا في إخراج الـ CLI.
- `test_detects_credentialed_url_key_and_tokens` — يغطي URL ببيانات دخول، ترويسة مفتاح خاص، معرّف AWS، ورمز GitHub.
- `test_exemption_marker_suppresses_dummy_value`.
- `test_excluded_paths_are_not_scanned_but_env_example_is` — يتحقق أن `.venv/` و`node_modules/` و`.env` و`*.pyc` مستبعدة، وأن `.env.example` ما زال يُفحص.
- `test_current_repository_has_no_findings`.

### الأوامر والنتائج الفعلية

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider tests/test_secret_scanner.py
.....                                                                    [100%]

.venv/bin/python scripts/check_no_secrets.py
No secret patterns found in repository sources.
exit=0
```

عند حقن سر وهمي في ملف اختبار، المخرج كان كالتالي فقط دون قيمة السر:

```text
Secret-pattern findings: 1
leak.py:1 [quoted-secret-assignment]
Matched values are intentionally not printed.
```

### ما بقي دون حل

الفحص يعتمد على أنماط معروفة ولا يكتشف كل صيغ الأسرار أو الأسرار عالية العشوائية بدون اسم حساس. الاستثناء الصريح يعتمد على مراجعة الـ PR. لم يُفحص كل سجل GitHub Actions سطراً بسطر، لكن الفاحص نفسه لا يمكنه طباعة القيم بعد الآن.

---

## 6. حماية فرع `main` — Issue #14

### المشكلة الأصلية

محاولة القراءة/الكتابة إلى إعدادات حماية الفرع أعادت `403 Resource not accessible by integration`. الوثيقة وحدها لا تثبت تطبيق الإعدادات.

### الملفات المعدّلة

- `docs/phase-1/branch-protection.md` — أُضيفت الإعدادات المطلوبة بدقة، وخطوات GitHub UI، وأمر `gh api` الذي يجب أن ينفّذه مالك المستودع، وأمر تحقق بنتيجة متوقعة.
- تعليق على Issue #14 برقم `7146240607` يرسل التعليمات ويُبقي الإشارة مفتوحة.

### Commit

`9ec073f docs(#14): give owner exact main protection instructions`

### الاختبار الذي يثبت الحل

لا يوجد اختبار آلي محلي لأن الصلاحية على GitHub غائبة. أُضيف أمر تحقق يجب أن ينفّذه المالك:

```bash
gh api repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection \
  --jq '{strict: .required_status_checks.strict, checks: .required_status_checks.contexts,
         approvals: .required_pull_request_reviews.required_approving_review_count,
         enforce_admins: .enforce_admins.enabled}'
```

النتيجة المتوقعة: `strict=true`, `checks=[lint,test,security]`, `approvals=1`, `enforce_admins=true`.

### الأوامر والنتائج الفعلية

لم تُجرَ أي محاولة جديدة لتجاوز الصلاحيات أثناء المعالجة. الحالة المعروفة ما زالت `403`، وIssue #14 ما زال مفتوحاً.

### ما بقي دون حل

حماية الفرع نفسها **لم تُطبّق**. هذا يعتمد على مالك المستودع. حتى ذلك الحين لا يُدمج أي PR إلى `main`، بما في ذلك PR #15.

---

## 7. أدلة التحقق النهائية على HEAD

| الفحص | الأمر | النتيجة الفعلية |
|---|---|---|
| كل الاختبارات | `PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -o addopts='' -q -p no:cacheprovider` | `33 passed, 2 warnings in 5.45s` |
| Ruff | `.venv/bin/ruff check apps/api tests scripts` | `All checks passed!` |
| Mypy | `.venv/bin/mypy apps/api/app` | `Success: no issues found in 13 source files` |
| Bandit | `.venv/bin/bandit -q -r apps/api/app -ll` | exit `0` |
| فاحص الأسرار | `.venv/bin/python scripts/check_no_secrets.py` | `No secret patterns found in repository sources.` exit `0` |
| Web typecheck | `npm --prefix apps/web run typecheck` | `tsc --noEmit`، exit `0` |
| Web build | `npm --prefix apps/web run build` | `✓ Generating static pages (4/4)`، exit `0` |
| CI push | `gh run watch 45501189086 --exit-status` | `conclusion=success`؛ الوظائف `lint`, `test`, `security` كلها `success` |
| CI pull_request | `gh run list --repo ... --limit 8` | run `#45501196642` على نفس HEAD: `completed success` |
| فحوص PR #15 | `gh pr view 15 --json statusCheckRollup` | ستة سجلات `SUCCESS` (ثلاث وظائف لكل من runّين) |
| HEAD | `git rev-parse HEAD` | `9ec073f9ca9adb2c60100553ba26cbfd114f7034` |
| `main` | `git rev-parse main origin/main` | `7820f29893815562613dd9c72ea4b0e51b956df3` لكليهما، لم يتغير |
| الشجرة | `git status --short --branch` | نظيفة ومتزامنة مع origin للفرع الحالي |
| PR #15 | `gh pr view 15 --json state,isDraft,mergedAt,mergeCommit` | `OPEN`, `isDraft=true`, `mergedAt=null`, `mergeCommit=null` |

تحذيرات غير حاجزة ما زالت موجودة: `Node.js 20 is deprecated ... actions/checkout@v4, actions/setup-python@v5` في GitHub Actions، و`StarletteDeprecationWarning` عند استخدام `TestClient` محلياً. لم تُفشل أي وظيفة.

## 8. نقاط بقيت دون حل صراحةً

1. **حماية فرع `main`** — تحتاج صلاحية إدارية لدى مالك المستودع؛ Issue #14 مفتوح.
2. **تطابق بيئة الإنتاج** — لم يُجرَ نشر أو فحص لـ TLS/النسخ الاحتياطي/نسخة PostgreSQL الفعلية؛ كان Testing على `pgserver` مؤقت.
3. **مراجعة كل سجلات CI سطراً بسطر** — الفاحص لا يطبع القيم الآن، لكن مراجعة سجلات GitHub التاريخية لم تتم بالكامل.
4. **قواعد الموافقة على مستوى المنتج** — لا توجد نقاط نهاية موافقة في Phase 1؛ لم يُبدأ Phase 2.
5. **إدارة جلسات شاملة** — لا يوجد إبطال لكل جلسات المستخدم أو تدوير رموز؛ لم تُضف لأنها outside نطاق المعالجة.

## 9. إعلان التوقف

انتهت أعمال المعالجة والتقرير عند هذا الحد. **لم أُعلن اعتماد Phase 1**، ولم أبدأ Phase 2، ولم أدمج PR #15، ولم أعدّل `main`، ولم أنفّذ أي نشر إنتاجي أو إنفاق مالي.
