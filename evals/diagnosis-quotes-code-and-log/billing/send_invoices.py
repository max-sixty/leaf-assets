"""Nightly invoice run: render each due invoice, email it, and mark it sent."""

import logging

from billing import db, mailer, render
from billing.retry import retry

log = logging.getLogger("invoice_run")

BATCH_SIZE = 200


def due_invoices(conn, period):
    return conn.execute(
        "SELECT id, customer_id, email FROM invoices"
        " WHERE period = %s AND sent_at IS NULL"
        " ORDER BY id",
        (period,),
    ).fetchall()


@retry(attempts=3, backoff_seconds=20, on=(mailer.MailerError, db.OperationalError))
def deliver(conn, invoice):
    pdf = render.invoice_pdf(invoice.id)
    message_id = mailer.send(
        to=invoice.email,
        subject=f"Your invoice {invoice.id}",
        attachment=pdf,
    )
    log.info("sent invoice=%s customer=%s message=%s", invoice.id, invoice.customer_id, message_id)
    conn.execute(
        "UPDATE invoices SET sent_at = now(), message_id = %s WHERE id = %s",
        (message_id, invoice.id),
        timeout_seconds=5,
    )
    log.info("marked invoice=%s sent", invoice.id)


def run(period):
    with db.connect() as conn:
        invoices = due_invoices(conn, period)
        log.info("run period=%s due=%d", period, len(invoices))
        for start in range(0, len(invoices), BATCH_SIZE):
            batch = invoices[start : start + BATCH_SIZE]
            for invoice in batch:
                try:
                    deliver(conn, invoice)
                except Exception:
                    log.exception("gave up on invoice=%s", invoice.id)
            conn.commit()
        log.info("run period=%s done", period)
