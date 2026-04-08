from __future__ import annotations

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS brand_profiles (
        id TEXT PRIMARY KEY,
        brand_name TEXT NOT NULL,
        voice_style TEXT NOT NULL DEFAULT '',
        preferred_vocabulary TEXT NOT NULL DEFAULT '[]',
        banned_phrases TEXT NOT NULL DEFAULT '[]',
        signature_patterns TEXT NOT NULL DEFAULT '[]',
        default_cta_style TEXT NOT NULL DEFAULT '',
        audience_notes TEXT NOT NULL DEFAULT '',
        positioning TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaigns (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        goal TEXT NOT NULL,
        target_audience TEXT NOT NULL DEFAULT '',
        brand_profile_id TEXT,
        brand_voice TEXT NOT NULL DEFAULT '',
        offer_summary TEXT NOT NULL DEFAULT '',
        strategy_summary TEXT NOT NULL DEFAULT '',
        content_mix TEXT NOT NULL DEFAULT '{}',
        posting_frequency TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (brand_profile_id) REFERENCES brand_profiles(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS campaign_variants (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        variant_name TEXT NOT NULL,
        prompt_snapshot TEXT NOT NULL DEFAULT '',
        generated_text TEXT NOT NULL DEFAULT '',
        cta TEXT NOT NULL DEFAULT '',
        hashtags TEXT NOT NULL DEFAULT '[]',
        score REAL NOT NULL DEFAULT 0,
        experiment_group TEXT NOT NULL DEFAULT '',
        approval_status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS templates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT '',
        platform TEXT NOT NULL DEFAULT '',
        template_text TEXT NOT NULL,
        tone TEXT NOT NULL DEFAULT '',
        cta_style TEXT NOT NULL DEFAULT '',
        score REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS scheduled_jobs (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        variant_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        run_at TEXT NOT NULL,
        timezone TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        retry_count INTEGER NOT NULL DEFAULT 0,
        last_error TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
        FOREIGN KEY (variant_id) REFERENCES campaign_variants(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS delivery_logs (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        request_payload TEXT NOT NULL DEFAULT '{}',
        response_payload TEXT NOT NULL DEFAULT '{}',
        status TEXT NOT NULL,
        external_post_id TEXT NOT NULL DEFAULT '',
        execution_mode TEXT NOT NULL DEFAULT 'dry_run',
        created_at TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES scheduled_jobs(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS performance_events (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        variant_id TEXT,
        platform TEXT NOT NULL,
        metric_type TEXT NOT NULL,
        metric_value REAL NOT NULL DEFAULT 0,
        source TEXT NOT NULL DEFAULT 'manual',
        note TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
        FOREIGN KEY (variant_id) REFERENCES campaign_variants(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS experiment_runs (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        variant_a_id TEXT NOT NULL,
        variant_b_id TEXT NOT NULL,
        winner_variant_id TEXT,
        decision_reason TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
        FOREIGN KEY (variant_a_id) REFERENCES campaign_variants(id) ON DELETE CASCADE,
        FOREIGN KEY (variant_b_id) REFERENCES campaign_variants(id) ON DELETE CASCADE,
        FOREIGN KEY (winner_variant_id) REFERENCES campaign_variants(id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS channel_credentials (
        id TEXT PRIMARY KEY,
        platform TEXT NOT NULL,
        account_label TEXT NOT NULL,
        encrypted_secret_blob TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
]


INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_brand_profiles_name ON brand_profiles(brand_name)",
    "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)",
    "CREATE INDEX IF NOT EXISTS idx_campaigns_brand_profile_id ON campaigns(brand_profile_id)",
    "CREATE INDEX IF NOT EXISTS idx_variants_campaign_platform ON campaign_variants(campaign_id, platform)",
    "CREATE INDEX IF NOT EXISTS idx_variants_approval_status ON campaign_variants(approval_status)",
    "CREATE INDEX IF NOT EXISTS idx_templates_platform ON templates(platform)",
    "CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_run_at_status ON scheduled_jobs(run_at, status)",
    "CREATE INDEX IF NOT EXISTS idx_delivery_logs_job_id ON delivery_logs(job_id)",
    "CREATE INDEX IF NOT EXISTS idx_performance_events_campaign_platform ON performance_events(campaign_id, platform)",
    "CREATE INDEX IF NOT EXISTS idx_experiment_runs_campaign_id ON experiment_runs(campaign_id)",
    "CREATE INDEX IF NOT EXISTS idx_channel_credentials_platform ON channel_credentials(platform)",
]
