# Sanctum Sanctorum Bookstore — Project Notes

### Live Deployment
- **Live URL:** https://merkle-science-assignment.vercel.app/
- **Credentials to try the UI:**
  - Enter member ID `1` to act as **Wong Li** (`supreme` tier — unlimited loans, 15% discount, unrestricted book access).
  - Enter member ID `2` to act as **Christine Palmer** (`master` tier).
  - Enter member ID `4` to act as **Sara Lin** (`apprentice` tier — tests tier limits and restrictions).

---

### What Was Finished
- **Books**: ISBN-13 checksum validation and normalization, 409 on duplicates, field patching, search/filter/sort/pagination query builder.
- **Members**: Email normalization, unique email checks (409), order history, active/overdue loan counts, and member stats.
- **Orders**: All-or-nothing stock reservation, tier discounts + volume discounts, payment transition, cancellation stock restoration.
- **Loans**: Complete loan model schema, borrow limits by tier, overdue restrictions, return logic, and day-ceiling late fee calculation.
- **Reports**: Best-sellers endpoint aggregating quantities across `paid` orders.
- **Test Suite**: 202 / 202 tests passing (`uv run pytest`).
- **Production Deployment**: Hosted on Vercel with Supabase PostgreSQL.

---

### Architectural Decisions & Trade-offs
1. **Layering & Separation of Concerns**: Kept routers minimal (HTTP parsing, calling service functions, returning schemas). All business logic, transaction boundaries, and status calculations live inside `app/services/`.
2. **Read-time Computed Loan Status**: Rather than running background cron jobs or database triggers to mark loans overdue, loan status is evaluated dynamically at read time (`active`, `overdue`, `returned`) comparing `due_at` against `now`. This keeps writes minimal and avoids state drift.
3. **Transactional Order Placement**: Order validation and stock decrements occur in an atomic transaction. If stock is insufficient or a book is restricted, the entire operation aborts without partial deductions.
4. **Database Abstraction**: `app/db.py` uses Supabase PostgreSQL in production while maintaining seamless zero-config fallback to in-memory SQLite for local testing, honoring the hard rule that tests run offline.

---

### Spec Observations & Decisions
- **Title Sorting**: SQLite and PostgreSQL handle mixed-case sorting differently by default. Followed the spec guidance to accept database-native ordering while ensuring ID asc breaks ties consistently.
- **Due Date Boundary**: The spec strictly defines that a loan returned at exactly `due_at` is active with 0 late fee; used strict inequality (`now > due_at`) to ensure no premature fees.

---

## AI Usage
- **Tools**: Google DeepMind Antigravity / Gemini coding assistant.
- **Usage**: Scaffolding service functions against SPEC rules, writing repetitive schema validators, and rubber-ducking Supabase pooler configurations.
- **Where AI was unhelpful/wrong**: When configuring PostgreSQL, the AI initially attempted to pass `check_same_thread: False` to the Postgres engine (which is SQLite-only and throws an error in `psycopg2`). Additionally, it initially tried connecting to Supabase via direct IPv6 hostnames which failed on IPv4 networks; I had to override it to configure the Supabase IPv4 connection pooler (`aws-0-ap-southeast-1.pooler.supabase.com:5432`) instead.
