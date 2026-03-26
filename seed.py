"""
Seed script — Creates 2 users with separate financial data + cross-user community posts.
User 1: Priya Fashions (priya@thriftey.com / demo1234)
User 2: Arjun Textiles (arjun@thriftey.com / demo1234)
"""

from database import engine, SessionLocal
import models
from routers.auth import get_password_hash
from datetime import date, timedelta, datetime
from utils.crypto import encrypt_sensitive_string
import random

def seed():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    today = date.today()
    random.seed(42)

    # ═══════════════════════════════════════════════
    #  BUSINESS 1 — Priya Fashions (Fashion Reseller)
    # ═══════════════════════════════════════════════
    b1 = models.Business(name="Priya Fashions", gst_number=encrypt_sensitive_string("27AAAPA1234A1Z5"), currency="INR", onboarding_completed=True)
    db.add(b1)
    db.commit()
    db.refresh(b1)

    u1 = models.User(business_id=b1.id, email="priya@thriftey.com", hashed_password=get_password_hash("demo1234"))
    db.add(u1)

    # Obligations — 8 items across suppliers, utilities, employees
    b1_obligations = [
        models.Obligation(business_id=b1.id, counterparty="Fabric World", counterparty_type="supplier", amount=45000, due_date=today + timedelta(days=5), penalty_risk=0.8, flexibility=0.2, urgency=0.9),
        models.Obligation(business_id=b1.id, counterparty="Button & Lace Co", counterparty_type="supplier", amount=12000, due_date=today + timedelta(days=15), penalty_risk=0.5, flexibility=0.5, urgency=0.6),
        models.Obligation(business_id=b1.id, counterparty="Silk Express", counterparty_type="supplier", amount=85000, due_date=today + timedelta(days=28), penalty_risk=0.4, flexibility=0.6, urgency=0.4),
        models.Obligation(business_id=b1.id, counterparty="Tamil Nadu EB", counterparty_type="utility", amount=8000, due_date=today + timedelta(days=10), penalty_risk=0.9, flexibility=0.0, urgency=0.95),
        models.Obligation(business_id=b1.id, counterparty="Airtel Broadband", counterparty_type="utility", amount=5000, due_date=today + timedelta(days=12), penalty_risk=0.7, flexibility=0.1, urgency=0.8),
        models.Obligation(business_id=b1.id, counterparty="Meena (Tailor)", counterparty_type="employee", amount=25000, due_date=today + timedelta(days=2), penalty_risk=0.1, flexibility=0.5, urgency=0.8),
        models.Obligation(business_id=b1.id, counterparty="Ravi (Designer)", counterparty_type="employee", amount=30000, due_date=today + timedelta(days=2), penalty_risk=0.1, flexibility=0.5, urgency=0.8),
        models.Obligation(business_id=b1.id, counterparty="Lakshmi (Helper)", counterparty_type="employee", amount=18000, due_date=today + timedelta(days=2), penalty_risk=0.1, flexibility=0.5, urgency=0.8),
    ]
    db.add_all(b1_obligations)

    # Receivables
    b1_receivables = [
        models.Receivable(business_id=b1.id, counterparty="Meesho Payout", amount=120000, expected_date=today + timedelta(days=7), confidence=0.85),
        models.Receivable(business_id=b1.id, counterparty="Flipkart Settlement", amount=45000, expected_date=today + timedelta(days=14), confidence=0.9),
        models.Receivable(business_id=b1.id, counterparty="Walk-in Client (Overdue)", amount=20000, expected_date=today - timedelta(days=2), confidence=0.5),
        models.Receivable(business_id=b1.id, counterparty="Retail Counter Sales", amount=50000, expected_date=today + timedelta(days=21), confidence=0.7),
    ]
    db.add_all(b1_receivables)

    # Transactions — 45 records over 90 days
    for i in range(45):
        txn_date = today - timedelta(days=random.randint(0, 90))
        is_in = random.choice([True, False])
        db.add(models.Transaction(
            business_id=b1.id, date=txn_date,
            amount=round(random.uniform(5000, 50000), 2),
            type="inflow" if is_in else "outflow",
            description=f"{'Sale' if is_in else 'Expense'} #{i+1}",
        ))

    # Cash position
    db.add(models.CashPosition(business_id=b1.id, balance=147500.0, as_of_date=today))

    # GST Reminders
    db.add_all([
        models.GSTReminder(business_id=b1.id, form_name="GSTR-1", deadline_day=11, notes="Sales return"),
        models.GSTReminder(business_id=b1.id, form_name="GSTR-3B", deadline_day=20, notes="Summary return"),
    ])

    # ═══════════════════════════════════════════════
    #  BUSINESS 2 — Arjun Textiles (Fabric Wholesaler)
    # ═══════════════════════════════════════════════
    b2 = models.Business(name="Arjun Textiles", gst_number=encrypt_sensitive_string("33BBBPB5678B2Z8"), currency="INR", onboarding_completed=True)
    db.add(b2)
    db.commit()
    db.refresh(b2)

    u2 = models.User(business_id=b2.id, email="arjun@thriftey.com", hashed_password=get_password_hash("demo1234"))
    db.add(u2)

    # Obligations — 6 items (different profile from Priya)
    b2_obligations = [
        models.Obligation(business_id=b2.id, counterparty="Cotton Mills Ltd", counterparty_type="supplier", amount=180000, due_date=today + timedelta(days=3), penalty_risk=0.9, flexibility=0.1, urgency=0.95),
        models.Obligation(business_id=b2.id, counterparty="Dye & Print Works", counterparty_type="supplier", amount=35000, due_date=today + timedelta(days=10), penalty_risk=0.6, flexibility=0.4, urgency=0.7),
        models.Obligation(business_id=b2.id, counterparty="TNEB Commercial", counterparty_type="utility", amount=15000, due_date=today + timedelta(days=8), penalty_risk=0.85, flexibility=0.0, urgency=0.9),
        models.Obligation(business_id=b2.id, counterparty="Shop Rent - T.Nagar", counterparty_type="rent", amount=42000, due_date=today + timedelta(days=1), penalty_risk=0.3, flexibility=0.2, urgency=0.7),
        models.Obligation(business_id=b2.id, counterparty="Kumar (Manager)", counterparty_type="employee", amount=45000, due_date=today + timedelta(days=4), penalty_risk=0.1, flexibility=0.4, urgency=0.85),
        models.Obligation(business_id=b2.id, counterparty="GST Q3 Payment", counterparty_type="government", amount=28000, due_date=today + timedelta(days=6), penalty_risk=0.95, flexibility=0.0, urgency=0.99),
    ]
    db.add_all(b2_obligations)

    # Receivables
    b2_receivables = [
        models.Receivable(business_id=b2.id, counterparty="Priya Fashions (Client)", amount=75000, expected_date=today + timedelta(days=5), confidence=0.8),
        models.Receivable(business_id=b2.id, counterparty="Chennai Sarees Inc", amount=110000, expected_date=today + timedelta(days=12), confidence=0.75),
        models.Receivable(business_id=b2.id, counterparty="Myntra Bulk Order", amount=90000, expected_date=today + timedelta(days=20), confidence=0.6),
    ]
    db.add_all(b2_receivables)

    # Transactions — 30 records
    for i in range(30):
        txn_date = today - timedelta(days=random.randint(0, 90))
        is_in = random.choice([True, False])
        db.add(models.Transaction(
            business_id=b2.id, date=txn_date,
            amount=round(random.uniform(10000, 80000), 2),
            type="inflow" if is_in else "outflow",
            description=f"{'Wholesale sale' if is_in else 'Purchase'} #{i+1}",
        ))

    # Cash position — tighter than Priya
    db.add(models.CashPosition(business_id=b2.id, balance=95000.0, as_of_date=today))

    # GST Reminders
    db.add_all([
        models.GSTReminder(business_id=b2.id, form_name="GSTR-1", deadline_day=11, notes="Sales return"),
        models.GSTReminder(business_id=b2.id, form_name="GSTR-3B", deadline_day=20, notes="Summary return"),
    ])

    # ═══════════════════════════════════════════════
    #  COMMUNITY FORUM — Cross-user interaction
    # ═══════════════════════════════════════════════

    # Priya's posts
    p1 = models.ForumPost(business_id=b1.id, title="Tips for managing cash flow during festival season?",
        content="Diwali orders are pouring in but my suppliers want advance payment. How do you handle the cash crunch between receiving orders and getting paid? Any strategies that worked for you?",
        category="cash_flow", created_at=datetime(2026, 3, 23, 10, 30))
    p2 = models.ForumPost(business_id=b1.id, title="GSTR-1 filing changes this quarter",
        content="Has anyone noticed the new fields in the GSTR-1 form? The HSN summary section seems different. Would love to hear if others have figured out the updates.",
        category="gst", created_at=datetime(2026, 3, 21, 14, 15))
    p3 = models.ForumPost(business_id=b1.id, title="Best practices for supplier negotiations",
        content="I need to extend payment terms with my fabric supplier without damaging our 5-year relationship. They've always been reliable. What approach has worked for you?",
        category="suppliers", created_at=datetime(2026, 3, 25, 9, 0))

    # Arjun's posts
    p4 = models.ForumPost(business_id=b2.id, title="Wholesale credit terms - what's standard?",
        content="I'm a fabric wholesaler and many of my retail clients expect 30-45 day credit. But my raw material suppliers want payment in 15 days. How do other wholesalers bridge this gap?",
        category="cash_flow", created_at=datetime(2026, 3, 24, 11, 45))
    p5 = models.ForumPost(business_id=b2.id, title="Tracking multiple GST registrations",
        content="I have branches in 3 states and managing GSTR-1 and GSTR-3B for each is becoming overwhelming. Any tools or workflows that help?",
        category="gst", created_at=datetime(2026, 3, 22, 16, 30))

    db.add_all([p1, p2, p3, p4, p5])
    db.commit()

    # Cross-user replies — Arjun replies to Priya, and vice versa
    replies = [
        # Arjun replies to Priya's cash flow post
        models.ForumReply(post_id=p1.id, business_id=b2.id,
            content="I face the exact same problem as a wholesaler! What works for me is negotiating 50% advance with clients and using that to cover supplier payments. Also, Meesho payouts are usually reliable — you can plan around their cycle.",
            created_at=datetime(2026, 3, 23, 15, 20)),

        # Priya replies to Arjun's credit terms post
        models.ForumReply(post_id=p4.id, business_id=b1.id,
            content="As a retailer, I appreciate wholesalers who offer flexible terms! Maybe you could offer 2% discount for 15-day payment? That motivates us to pay faster. I'd definitely take that deal.",
            created_at=datetime(2026, 3, 24, 18, 10)),

        # Arjun replies to Priya's supplier negotiation post
        models.ForumReply(post_id=p3.id, business_id=b2.id,
            content="For long-term suppliers, I've found that being upfront about your situation works best. Share your payment schedule and commit to a specific date. They'd rather wait a week with certainty than wonder if they'll get paid.",
            created_at=datetime(2026, 3, 25, 12, 30)),

        # Priya replies to Arjun's GST post
        models.ForumReply(post_id=p5.id, business_id=b1.id,
            content="I only have one GSTN but I've heard ClearTax handles multi-state really well. Their bulk upload feature might save you hours. Worth checking out!",
            created_at=datetime(2026, 3, 23, 8, 45)),

        # Priya also replies to her own cash flow post (adding info)
        models.ForumReply(post_id=p1.id, business_id=b1.id,
            content="Update: I tried requesting partial advance from my Meesho orders and it actually worked! Got ₹50K released early. Thanks for the suggestions everyone.",
            created_at=datetime(2026, 3, 25, 20, 0)),
    ]
    db.add_all(replies)
    db.commit()

    print(f"✅ Seeded successfully!")
    print(f"   Business 1: {b1.name} (ID: {b1.id}) — priya@thriftey.com / demo1234")
    print(f"   Business 2: {b2.name} (ID: {b2.id}) — arjun@thriftey.com / demo1234")
    print(f"   Forum: {5} posts, {len(replies)} replies")

if __name__ == "__main__":
    seed()
