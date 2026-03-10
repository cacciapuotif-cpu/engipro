"""
Add deadlines table.

Migration for Deadline model.
Revision ID: 001
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime, timezone

# This migration is auto-generated from model: app.models.deadline.Deadline
# Created at: 2026-03-10

"""
SQL for manual creation:

CREATE TABLE deadlines (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    worker_id INTEGER,
    tipo VARCHAR NOT NULL,
    titolo VARCHAR(255) NOT NULL,
    descrizione VARCHAR(1000),
    data_scadenza DATE NOT NULL,
    data_completamento DATE,
    stato VARCHAR NOT NULL DEFAULT 'PENDING',
    priorita VARCHAR NOT NULL DEFAULT 'MEDIUM',
    giorni_preavviso INTEGER DEFAULT 7 NOT NULL,
    last_notification_sent TIMESTAMP WITH TIME ZONE,
    notification_count INTEGER DEFAULT 0 NOT NULL,
    assegnato_a INTEGER,
    note VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (worker_id) REFERENCES workers(id),
    FOREIGN KEY (assegnato_a) REFERENCES workers(id)
);

CREATE INDEX idx_deadlines_company_id ON deadlines(company_id);
CREATE INDEX idx_deadlines_worker_id ON deadlines(worker_id);
CREATE INDEX idx_deadlines_data_scadenza ON deadlines(data_scadenza);
CREATE INDEX idx_deadlines_stato ON deadlines(stato);
CREATE INDEX idx_deadlines_tipo ON deadlines(tipo);
"""

def upgrade():
    """Create deadlines table."""
    pass  # Table is auto-created by SQLAlchemy Base.metadata.create_all()


def downgrade():
    """Drop deadlines table."""
    pass  # Table is auto-dropped when Base.metadata is cleared
