# تدقيق القبول المستقل — المرحلة الأولى (Phase 1)

تاريخ التدقيق: 2026-11-24 (UTC)  
المستودع: `mamourgroupe-ctrl/ai-growth-operator`  
الفرع: `arena/5dc98770-ai-growth-operator`  
HEAD: `1c10f5c590b35e78102e7a26cb695d239812a62d`  
الأساس/الفرع الرئيسي: `7820f29893815562613dd9c72ea4b0e51b956df3`

## 1. نطاق التدقيق وقيوده

- هذا تدقيق **قراءة فقط** باستثناء إنشاء هذا الملف. لم أُصلح findings، ولم أُنشئ commits، ولم أدمج PR، ولم أغلق issues، ولم أبدأ المرحلة الثانية.
- لم أعد executing أي شيء على `main`؛ `main` و`origin/main` لم يتغيرا.
- GitHub connector غير متصل؛ استخدمت `gh` CLI. لا توجد صلاحية إدارية على إعدادات المستودع: `GET /repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection` أعاد `403 Resource not accessible by integration`. لذلك **لا يمكن اعتبار وثائق `docs/phase-1/branch-protection.md` دليلاً على تفعيل حماية الفرع فعلياً**.
- قاعدة البيانات المستخدمة للتدقيق هي PostgreSQL حقيقي مؤقت عبر `pgserver` (لا نظام PostgreSQL مثبّت ولا Docker في البيئة). هذا يكفي لتصحيح الرولات وسياسات RLS، لكنه **ليس** دليلاً على تطابق بيئة الإنتاج (النسخة، TLS، النسخ الاحتياطي، إدارة الأسرار، إلخ).
- رموز الحالة: `PASS` = مُتحقق منه، `PARTIAL` = جزئي/فجوة، `FAIL` = فشل مُلاحظ، `NOT VERIFIED` = تعذّر التحقق.

---

## 2. سلامة Git والفروع — Git Integrity

| المعيار | الأمر / المصدر | النتيجة الفعلية | الحالة |
|---|---|---|---|
| الفرع الصحيح نشط | `git branch --show-current` | `arena/5dc98770-ai-growth-operator` | PASS |
| HEAD دون تغيير | `git rev-parse HEAD` | `1c10f5c590b35e78102e7a26cb695d239812a62d` | PASS |
| `main` و`origin/main` لم يمسّا | `git rev-parse main origin/main` | كلاهما `7820f29893815562613dd9c72ea4b0e51b956df3` | PASS |
| سلسلة commits واضحة | `git rev-list --count 7820f29..HEAD` | `16` commit | PASS |
| لا تعديلات غير مُودَعة | `git status --short --branch` | `## arena/5dc98770-ai-growth-operator...origin/arena/5dc98770-ai-growth-operator` بدون أسطر ملفات معدّلة | PASS |
| PR #15 لم يُدمج | `gh pr view 15 --json state,isDraft,mergedAt,mergeCommit,baseRefName,headRefName` | `state=OPEN`, `isDraft=true`, `mergedAt=null`, `mergeCommit=null`, `baseRefName=main`, `headRefName=arena/5dc98770-ai-growth-operator` | PASS |
| حماية فرع `main` | `gh api repos/mamourgroupe-ctrl/ai-growth-operator/branches/main/protection` | `403 Resource not accessible by integration`؛ Issue #14 ما زال مفتوحاً | NOT VERIFIED |

> الخلاصة: الضمانات المحلية (Git/PR) سليمة. إعدادات GitHub نفسها خارج متناول الرمز المستخدم، لذلك لا يُقبل دليل توثيقي كبديل للتحقق.

---

## 3. التدقيق الأمني

### 3.1 جداول المستأجرين وسياسات RLS الفعلية

المصدر: `apps/api/migrations/versions/0001_initial.py:23-48` (دالة `_rls`)، واستعلام كتالوج PostgreSQL حقيقي بعد `alembic upgrade head`:

```sql
SELECT cl.relname, cl.relrowsecurity, cl.relforcerowsecurity,
       p.policyname, p.cmd, p.qual, p.with_check
FROM pg_class cl
JOIN pg_policies p ON p.schemaname='public' AND p.tablename=cl.relname
WHERE cl.relnamespace='public'::regnamespace AND cl.relkind='r';
```

النتيجة: خمسة جداول فقط تحمل سياسة `tenant_isolation`، وكلها `relrowsecurity=true` و`relforcerowsecurity=true` و`cmd=ALL`:

| الجدول | USING | WITH CHECK |
|---|---|---|
| `ai_generation_jobs` | `tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid` | نفس التعبير |
| `outbox_events` | `tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid` | نفس التعبير |
| `audit_logs` | `tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid` | نفس التعبير |
| `tenant_memberships` | `tenant_id = current_tenant_id OR user_id = current_user_id` | `tenant_id = current_tenant_id` |
| `tenants` | `id = current_tenant_id OR id IN (SELECT tenant_id FROM tenant_memberships WHERE user_id = current_user_id)` | `id = current_tenant_id` |

التعبير المُكتمل كما ظهر في `pg_policies`:

```text
tenants.USING: ((id = (NULLIF(current_setting('app.current_tenant_id'::text, true), ''::text))::uuid)
  OR (id IN (SELECT tenant_memberships.tenant_id FROM tenant_memberships
             WHERE tenant_memberships.user_id = (NULLIF(current_setting('app.current_user_id'::text, true), ''::text))::uuid))))
tenant_memberships.USING: ((tenant_id = current_tenant_id) OR (user_id = current_user_id))
```

الجداول `users` و`sessions` **لا تحمل سياسات RLS**؛ هي جداول هوية عامة (`global`)، ويجب أن تُطبّق قواعد الوصول إليها في طبقة التطبيق عبر `TenantMembership`. هذا تصميم مقصود ظاهراً في الكود، لكنه يعني أن العزل ليس شاملاً على مستوى قاعدة البيانات لكل الجداول.

| المعيار | الدليل | النتيجة الفعلية | الحالة |
|---|---|---|---|
| تعداد جداول المستأجرين وسياساتها | الكتالوج + `0001_initial.py` | 5 جداول RLS/FORCE بسياسة `tenant_isolation`؛ لا توجد سياسة على `users`/`sessions` | PASS للتعداد؛ PARTIAL للشمول |
| منع INSERT لtenant آخر | `tests/test_tenant_isolation.py::test_rls_with_check_rejects_insert_into_other_tenant` | `pytest.raises(ProgrammingError)` عند إدراج `ai_generation_jobs.tenant_id` الخاص بـ tenant B أثناء سياق tenant A | PASS |
| منع قراءة tenant آخر | `tests/test_tenant_isolation.py::test_direct_reads_with_application_role_are_tenant_scoped` | بدون سياق = `count(tenants)=0`; بسياق A = `[tenant_a]`; الاستعلام المباشر عن B = `0` | PASS |

### 3.2 رول التطبيق وسياق المعاملة

| المعيار | الدليل | النتيجة الفعلية | الحالة |
|---|---|---|---|
| `ago_app` ليس superuser ولا BYPASSRLS | `tests/test_tenant_isolation.py::test_application_role_is_not_superuser_or_bypassrls` + استعلام كتالوج مستقل: `SELECT rolsuper, rolbypassrls, rolcanlogin FROM pg_roles WHERE rolname='ago_app'` | `(False, False, True)` = `rolsuper=false`, `rolbypassrls=false`, `rolcanlogin=true` | PASS |
| إنشاء الرول في الاختبارات | `tests/conftest.py:24-33` | `CREATE ROLE ago_app LOGIN PASSWORD <random> NOSUPERUSER NOBYPASSRLS` | PASS |
| السياق داخل المعاملة فقط | `apps/api/app/db.py:22-26` يستدعي `set_config('app.current_tenant_id', ..., true)` و`set_config('app.current_user_id', ..., true)` | الوسيط الثالث `true` = `is_local`؛ أي أن القيمة ترتبط بالمعاملة الحالية | PASS |
| عدم تسريب السياق عبر pool | فحص مستقل: جلسة داخل معاملة عيّنت القيمة، ثم اتصال جديد من نفس الـ engine بعد `commit()` | داخل المعاملة: القيمة مضبوطة؛ بعدها في اتصال مجمّع: `''` | PASS |
| API يستخدم رول التطبيق في اختبارات CI | `tests/conftest.py:35-36` و`apps/api/app/config.py:7`, `apps/api/app/db.py:13-14` | `AGO_DATABASE_URL` = `admin_url` (superuser) و`AGO_APP_DATABASE_URL` = رول التطبيق. **`get_engine()` يقرأ `database_url` فقط**، و`app_database_url` غير مستخدم في كود التطبيق. اختبارات API تعمل بـ superuser؛ اختبارات RLS المباشرة تستخدم `app_engine` برول التطبيق | PARTIAL |
| تحقق يدوي إضافي برول التطبيق | تشغيل `TestClient` مع `AGO_DATABASE_URL=app_url` بعد `get_settings.cache_clear()` | `POST /auth/register` → 201، `GET /auth/me` → 200، `GET /organizations/{A}` بواسطة B → 404، `GET /organizations` لـ B يعرض مؤسسته فقط (1)، `GET /organizations/{A}` بواسطة A → 200 | PASS (خارج الأتمتة) |

> ** finding مهم:** الفجوة ليست في سياسة RLS نفسها، بل في توجيه الاتصال. يجب أن يكون `AGO_DATABASE_URL` المستخدم من قِبل التطبيق هو رول `ago_app` غير superuser في الإنتاج، وإلا تُجاوز RLS بواسطة superuser. `.env.example` لا يوضّح ذلك، ولا يوجد تحقق آلي في CI يمرّر مسار API عبر الرول غير الممتاز.

### 3.3 مراجعة مسارات منعcross-tenant واختباراتها

`tests/test_tenant_isolation.py`:

| الحالة | المسار / الإجراء | النتيجة المتوقعة والمُلاحظة |
|---|---|---|
| مستخدم B يقرأ مؤسسة A | `GET /organizations/{org_a}` | `404` |
| مستخدم B يقرأ مؤسسته | `GET /organizations/{org_b}` | `200` |
| B يضيفه المالك A كـ viewer ثم يحاول تعديل عضو | `PATCH /organizations/{org_a}/members/{owner_id}` مع CSRF مزوّر | `403` |
| RLS مباشر | `SELECT ... FROM tenants` مع/بدون سياق | عزل كامل كما هو موضح أعلاه |

`tests/test_rbac.py` (مسارات إضافية): `GET /organizations/{org}`، `PATCH /organizations/{org}`، `GET/POST /organizations/{org}/members`، `PATCH /organizations/{org}/members/{user}`. النتائج: editor يقرأ `200` لكنه مُنع من إضافة عضو وتعديل المؤسسة (`403`)؛ viewer يقرأ `200`؛ مستخدم من مؤسسة أخرى يحصل على `404`؛ owner وحده يضيف/يعدّل الأعضاء.

| المعيار | الحالة |
|---|---|
| تغطية منعcross-tenant على المسارات الأساسية | PARTIAL — المسارات المذكورة مغطاة، لكنها محدودة (لا توجد مسارات أعمال/وظائف بعد في Phase 1)، وتعتمد على superuser في اختبارات API |

### 3.4 المصادقة والجلسات وCSRF وArgon2id

| المعيار | الملف / الأمر | النتيجة الفعلية | الحالة |
|---|---|---|---|
| تجزئة كلمة المرور | `apps/api/app/security.py:9-17` + فحص مباشر `hash_password()` | البادئة `$argon2id$`، المعاملات `v=19 m=65536,t=3,p=4`؛ `verify_password` صحيح/خاطئ = `True/False` | PASS |
| الرموز والـ CSRF | `apps/api/app/security.py:20-38` | `secrets.token_urlsafe(32)` للجلسة والـ CSRF؛ تخزين `sha256` للرمز؛ مقارنة `hmac.compare_digest` | PASS |
| كوكي الجلسة | `apps/api/app/routers/auth.py:22-32` | `HttpOnly`, `SameSite=Lax`, `secure=AGO_COOKIE_SECURE` (افتراضي `True` في `config.py:11`), `max_age = TTL` | PASS |
| Register/Login/Logout | `tests/test_auth.py` | 201/200/204، بيانات خاطئة → 401 بصيغة `application/problem+json`، بريد مكرر → 409، تحقق خاطئ → 422 | PASS |
| CSRF على مسارات التغيير | `apps/api/app/auth.py:68-72`, `routers/auth.py:95-107`, `routers/organizations.py` | مطلوب على `POST /auth/logout`، `POST /organizations`، `PATCH /organizations/{id}`، `POST/PATCH /organizations/{id}/members...`; اختبار فقدان CSRF → 403 واختبار CSRF مزوّر → 403 | PASS |
| انتهاء الجلسة (idle وabsolute) | `apps/api/app/auth.py:36-62`; فحص يدوي: تعديل `sessions.expires_at` و`sessions.absolute_expires_at` إلى الماضي ثم `GET /auth/me` | في الحالتين: `401 Unauthorized`. قبل التعديل: `200` | PASS يدوياً؛ PARTIAL كأتمتة |
| إلغاء الجلسة | `POST /auth/logout` يضبط `revoked_at` ويحذف الكوكي؛ `tests/test_auth.py::test_login_and_logout_require_valid_credentials_and_csrf` | بعد logout: `GET /auth/me` → 401 | PASS للجلسة الحالية |
| إلغاء كل جلسات المستخدم / تدوير الرموز | بحث في `apps/api/app/routers/auth.py` و`auth.py` | لا توجد نقطة نهاية لذلك؛ لا يوجد اختبار آلي لانتهاء TTL/absolute TTL | PARTIAL |
| تجاوز الموافقة عبر API | لا توجد نقاط نهاية موافقة في Phase 1 | لا يمكن اختبار قاعدة "المالك وحده الموافق النهائي" هنا؛ أُجّل للمرحلة اللاحقة | NOT VERIFIED (خارج نطاق Phase 1) |

> ملاحظة: `login`/`register` عامان ولا يطلبان CSRF؛ هذا شائع للجلسات المعتمدة على كوكي `SameSite=Lax`، لكنه يبقي login-CSF خارج اختبارات Phase 1. لم أعتبره فشلاً، بل فجوة تغطية.

### 3.5 فحص الأسرار

`scripts/check_no_secrets.py` (كامل السلوك):

- `SCAN_DIRS = [ROOT/"apps/api/app", ROOT/"apps/web/app"]`
- `EXTENSIONS = {".py", ".ts", ".tsx", ".mjs"}`
- `PATTERN = re.compile(r"\b(SECRET_KEY|API_KEY|PASSWORD)\s*=\s*[\"'][^\"']+[\"']")`
- لا توجد قائمة استثناءات (skip list) داخل السكربت.

الأمر والنتيجة: `.venv/bin/python scripts/check_no_secrets.py` → `No hardcoded secret patterns in application source.` (exit 0).  
فحص أشمل داخل نطاق السكربت: لا أسرار ظاهرة في مخرجات الأوامر المحلية التي شغّلتها. لم أفحص سجلات GitHub بالكامل؛ لذلك يُذكر ذلك كتحقق جزئي.

| المعيار | الحالة |
|---|---|
| لا أسرار في كود التطبيق ضمن نطاق السكربت | PASS |
| تغطية السكربت لكل الملفات (tests/scripts/workflows/docs) وسجلات CI | PARTIAL — السكربت يفحص مجلدَي التطبيق فقط وبنمط ضيّق |

---

## 4. تدقيق CI

### 4.1 ملف CI كاملاً (` .github/workflows/ci.yml `)

```yaml
name: CI

on:
  push:
    branches: ["**"]
  pull_request:
    branches: ["**"]

jobs:
  lint:
    name: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -e ".[dev]"
      - run: ruff check apps/api tests
      - run: mypy apps/api/app
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: npm
          cache-dependency-path: apps/web/package-lock.json
      - run: npm --prefix apps/web ci
      - run: npm --prefix apps/web run typecheck

  test:
    name: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -e ".[dev]"
      - run: pytest -q

  security:
    name: security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -e ".[dev]"
      - run: bandit -r apps/api/app -ll
      - name: Check for hardcoded secrets
        run: python scripts/check_no_secrets.py
```

المحفّزات: `push` و`pull_request` على `["**"]` (أي كل الفروع). الوظائف: `lint`, `test`, `security`. لا توجد وظيفة `build` للـ web داخل CI؛ البناء تحقّقت منه محلياً فقط.

### 4.2 نتائج تنفيذ فعلية

| الفحص | الأمر | النتيجة الفعلية | الحالة |
|---|---|---|---|
| pytest | `PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -q -p no:cacheprovider` | `18 passed` (18 نقطة) | PASS |
| Ruff | `.venv/bin/ruff check apps/api tests scripts` | `All checks passed!` | PASS |
| Mypy | `.venv/bin/mypy apps/api/app` | `Success: no issues found in 13 source files` | PASS |
| Bandit | `.venv/bin/bandit -q -r apps/api/app -ll` | exit `0` | PASS |
| فاحص الأسرار | `.venv/bin/python scripts/check_no_secrets.py` | `No hardcoded secret patterns in application source.` | PASS |
| Web typecheck | `npm --prefix apps/web run typecheck` | `> tsc --noEmit`، exit `0` | PASS |
| Web build | `npm --prefix apps/web run build` | `✓ Generating static pages (4/4)`, exit `0`; `/` و`/_not-found` ثابتان | PASS |
|Health/API | طلبات سابقة على الـ preview: `curl /healthz` و`curl /openapi.json` | `{"status":"ok"}` وOpenAPI بعنوان `AI Growth Operator API` | PASS |
| تشغيل CI على HEAD | `gh run list --workflow CI --limit 6` | `#45425269970 pull_request 1c10f5c success` و`#45425251351 push 1c10f5c success` | PASS |
| فحوص PR #15 | `gh pr view 15 --json statusCheckRollup` | وظائف `lint`, `test`, `security` في_run `#45425269970` و`#45425251351` كلها `conclusion=SUCCESS` | PASS |

التحذيرات غير الحاجزة: ظهرت تنبيهات تقادم Node.js 20 في واجهة GitHub Actions أثناء تشغيلات سابقة، وتحذير `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated` محلياً أثناء اختبارات `TestClient`. لم تُفشل أي وظيفة. محاولة قراءة annotations عبر API أعادت 404 بصلاحية الرمز الحالية؛ لذلك لم أُثبت نص التنبيه من الـ API، بل من الملاحظة المباشرة أثناء التشغيل.

> ملاحظة منهجية: كانت هناك محاولة أولى لاستدعاء `tsc` عبر `npm --prefix apps/web exec -- tsc --noEmit --incremental false` ففشلت بسبب خيار CLI غير مدعوم في هذا الإصدار؛ ثم استخدمتُ البرنامج الرسمي `npm run typecheck` الذي نجح. لا علاقة للفشل الأول بكود المشروع.

---

## 5. تدقيق قاعدة البيانات والهجرات (migrations)

| المعيار | الدليل /_command_ | النتيجة الفعلية | الحالة |
|---|---|---|---|
| ملفات الهجرة موجودة | `apps/api/migrations/versions/0001_initial.py` | مراجعة واحدة `0001_initial`, `down_revision=None` | PASS |
| ترقية قاعدة فارغة | `command.upgrade(Config("alembic.ini"), "head")` على pgserver فارغ + رول `ago_app` | نجح؛ `SELECT version_num FROM alembic_version` → `0001_initial` | PASS |
| الرجوع إلى `base` | `command.downgrade(cfg, "base")` | **فشل**: `psycopg.errors.DependentObjectsStillExist: cannot drop table tenant_memberships because other objects depend on it` / `DETAIL: policy tenant_isolation on table tenants depends on table tenant_memberships` / `HINT: Use DROP ... CASCADE`. دالة `downgrade()` موجودة لكنها غير صالحة للتنفيذ | FAIL |
| المفاتيح الخارجية | استعلام `information_schema.referential_constraints` | 6 FKs: `jobs.tenant_id→tenants CASCADE`, `outbox.tenant_id→tenants CASCADE`, `memberships.tenant_id→tenants CASCADE`, `memberships.user_id→users CASCADE`, `sessions.user_id→users CASCADE`, `jobs.requested_by→users SET NULL` | PASS |
| قيود فريدة | `0001_initial.py` + `pg_indexes` | `uq_users_email_lower`, `uq_tenants_slug_lower`, `uq_jobs_tenant_idempotency (tenant_id,idempotency_key)`, `uq_outbox_aggregate_event (tenant_id,aggregate_id,event_type)`, `uq_sessions_token_hash` | PASS |
| فهارس الأداء | `pg_indexes` | 19 فهرساً بما فيها `ix_jobs_tenant_status_created`, `ix_jobs_queued`, `ix_outbox_tenant_status`, `ix_audit_logs_tenant_created`, `ix_tenant_memberships_user_id` | PASS |
| سلامة `audit_logs` | الكتالوج + `0001_initial.py:159-174` | `tenant_id` قابل للـ NULL ولا يملك FK إلى `tenants` | PARTIAL |
| منح الصلاحيات | `0001_initial.py:184-187`, `apps/api/migrations/env.py:38` | `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ago_app` و`GRANT USAGE ON SCHEMA public` | PASS |
| إنشاء رول التطبيق تلقائياً | بحث في الهجرة | لا يوجد `CREATE ROLE`؛ الرول يُفترض موجوداً ويُنشأ خارجياً (في الاختبارات بواسطة `conftest.py`) | PARTIAL |

### 5.1 الفجوات بين بيئة الاختبار والإنتاج

1. `pgserver` محلي مؤقت مقابل PostgreSQL مُدار في الإنتاج: لم يتم التحقق من إصدار الخادم، TLS، النسخ الاحتياطي، أو حدود الاتصال.
2. اختبارات API تمرّر `AGO_DATABASE_URL=admin_url` (superuser) إلى `get_engine()`؛ رول `ago_app` يُستخدم فقط في `app_engine` لاختبارات RLS المباشرة. انظر 3.2.
3. `app_database_url` مُعرّف في `Settings` و`.env.example` لكنه **غير مستخدم** في `apps/api/app/db.py`؛ هذا يسبب التباساً في النشر ويجب توضيحه بتمرير رول التطبيق في `AGO_DATABASE_URL` أو تعديل الكود (لم أُصلح شيئاً).
4. `downgrade` معطّل عملياً بسبب تبعية سياسة `tenants` على `tenant_memberships`.
5. `audit_logs.tenant_id` nullable وبلا FK، بينما بقية جداول المستأجرين لها FK CASCADE.
6. حماية فرع `main` غير مُتحقق منها عبر GitHub (403)؛ المستند وحده لا يكفي.
7. لا توجد نقطة نهاية موافقة/إلغاء موافقة في Phase 1، لذلك لم يتسنَّ التحقق من قاعدة "لا تجاوز للموافقة عبر API" product-level.

---

## 6. مصفوفة القبول النهائية

| # | المعيار | الدليل المختصر /_command_ | النتيجة الفعلية | الحالة |
|---|---|---|---|---|
| 1 | الفرع/HEAD/الأساس/PR/شجرة نظيفة | `git status`, `git rev-parse`, `gh pr view 15` | HEAD `1c10f5c`, main `7820f29`, 16 commit, PR OPEN draft unmerged, لا تعديلات | PASS |
| 2 | حماية فرع main | `gh api .../branches/main/protection` | 403؛ لا إثبات من GitHub | NOT VERIFIED |
| 3 | محفّزات CI ووظائفه | `.github/workflows/ci.yml` | push/PR `**`؛ lint/test/security | PASS |
| 4 | تشغيل CI فعلي على HEAD | `gh run view 15` / `gh run list` | #45425269970 و#45425251351 كلاهما success؛ 6 checks SUCCESS | PASS |
| 5 | فاحص الأسرار وتعديلاته | `scripts/check_no_secrets.py` + run security | لا استثناءات؛ `No hardcoded secret patterns...` | PASS |
| 6 | جودة Python محلياً | pytest/ruff/mypy/bandit | 18 passed / All checks / 13 files / exit 0 | PASS |
| 7 | جودة Web محلياً | `npm run typecheck` + `npm run build` | exit 0 / 4 صفحات مولّدة | PASS |
| 8 | تشغيل التطبيق | preview: `/healthz`, `/openapi.json`, `/` | 200 / OpenAPI / 200 | PASS |
| 9 | الهجرة من قاعدة فارغة | `alembic upgrade head` | `0001_initial` | PASS |
| 10 | دعم downgrade | `alembic downgrade base` | DependentObjectsStillExist | FAIL |
| 11 | RLS على جداول المستأجرين | كتالوج Postgres + 0001_initial | 5 جداول ENABLE+FORCE بسياسة `tenant_isolation` | PASS |
| 12 | رول التطبيق غير ممتاز | `pg_roles` + test | `(False, False, True)` | PASS |
| 13 | عزل سياق المعاملة وإعادة استخدام pool | `set_config(..., true)` + probe | داخل المعاملة مضبوط؛ بعدها `''` | PASS |
| 14 | RLS مُختبار برول التطبيق | `test_direct_reads_with_application_role_are_tenant_scoped` | نجح برول `ago_app` | PASS |
| 15 | مسار API تحت رول التطبيق في CI | `tests/conftest.py:35-36`, `db.py:13-14` | API يستخدم superuser؛ probe يدوي برول التطبيق نجح | PARTIAL |
| 16 | رفضcross-tenant | `test_tenant_isolation.py`, `test_rbac.py` + probe | 404/403 كما هو متوقع | PARTIAL (تغطية محدودة + superuser في CI) |
| 17 | المصادقة/CSRF/Argon2id | `tests/test_auth.py`, `security.py`, probe | argon2id، 401/403/409/201/204، انتهاء يدوي 401 | PARTIAL |
| 18 | إلغاء الجلسة | `POST /auth/logout` + test | الجلسة الحالية تُلغى (401 بعدها) | PASS |
| 19 | لا أسرار في الكود الممسوح | فاحص الأسرار | نظيف ضمن نطاق السكربت | PARTIAL (نطاق ضيّق) |
| 20 | لا أسرار في سجلات CI | مراجعة مخرجات محلية + تشغيلات GitHub | لم يُلاحظ تسريب محلياً؛ لم تُفحص كل السجلات | NOT VERIFIED |
| 21 | تطابق بيئة الاختبار والإنتاج | pgserver مقابل production | لم يتحقق؛ فجوات 5.1 | NOT VERIFIED |
| 22 | قواعد الموافقة/product-level | لا توجد endpoints بعد | خارج نطاق Phase 1 | NOT VERIFIED |

## 7. الخلاصة

الأساس الهندسي لـ Phase 1 موجود وقابل للعمل: التطبيق يُقلع، الهجرة تصعد على قاعدة فارغة، المصادقة والتسجيل وإنشاء المؤسسة وتغطية RBAC تعمل، وسياسات RLS مُطبّقة ومُختبرة برول `ago_app` غير superuser، وكل فحوص CI نجحت على HEAD.

لكن لا أُوصي باعتبار Phase 1 **مقبولاً بالكامل** قبل معالجة ما يلي:

1. `FAIL` — `alembic downgrade base` معطّل بسبب تبعية policy؛ يلزم `DROP POLICY` قبل إسقاط الجداول في `downgrade()`.
2. `PARTIAL` — API في الاختبارات يعمل بـ superuser عبر `AGO_DATABASE_URL`، و`app_database_url` غير مستخدم؛ يجب تثبيت مسار رول التطبيق في التطبيق/CI.
3. `PARTIAL` — انتهاء الجلسة تحقق يدوياً فقط، ولا توجد إدارة جلسات شاملة/تدوير.
4. `PARTIAL` — `audit_logs.tenant_id` بلا FK وقابل للـ NULL.
5. `NOT VERIFIED` — حماية فرع `main` على GitHub (403)، وتطابق بيئة الإنتاج، وسجلات CI الكاملة.

لم يُجرَ أي إصلاح أو تغيير في المستودع بموجب هذا التدقيق، باستثناء إنشاء هذا التقرير.
