"""Seeds realistic demo data for the InterviewStack dashboard/analytics UI.

Not part of the application - a one-off dev utility. Every row is written
through the real SQLAlchemy models (Interview/Transcript/Insight/PainPoint/
Embedding), so the dashboard/trends/explorer/search endpoints are exercising
genuine aggregation queries over genuine Postgres rows. The realism gap this
closes: MockAIProvider (used for testing the async pipeline without an LLM
key) always returns the same category/sentiment/empty lists for every
transcript, which would render as a single flat bar on every chart. The
sample content below is invented, same as any seed script for any demo app -
the charts themselves compute everything live from what's actually stored.

Run with: python -m scripts.seed_demo_data (from backend/, venv activated).
"""

import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.models.embedding import Embedding  # noqa: E402
from app.models.insight import CustomerSentiment, Insight, PainPoint, PainPointCategory  # noqa: E402
from app.models.interview import InputType, Interview, InterviewStatus, Transcript  # noqa: E402
from app.services.ai.mock_provider import _deterministic_unit_vector  # noqa: E402

PPC = PainPointCategory
CS = CustomerSentiment

# (title, days_ago, customer_type, sentiment, [(category, description)],
#  feature_requests, competitors, action_items, notable_quotes, summary, transcript)
COMPLETED_INTERVIEWS = [
    (
        "Acme Corp - Quarterly Review", 2, "enterprise", CS.NEGATIVE,
        [(PPC.PRICING, "Pricing tier jumped 40% at renewal with no advance warning, hard to justify to finance.")],
        ["Custom reporting exports"], ["Salesforce"],
        ["Send updated pricing breakdown by Friday", "Loop in finance stakeholder before next renewal"],
        ["We almost switched to Salesforce over this pricing jump."],
        "Acme is frustrated by an unannounced 40% price increase at renewal and is now comparing costs against Salesforce. They still value the product but want pricing transparency going forward.",
        "Look, the renewal came in and it was almost 40% higher than last year with zero warning. I had to explain that to finance and it wasn't a fun conversation. We've been happy with the product itself, honestly, but if this keeps happening we're going to seriously look at Salesforce again. We just need to know changes like this are coming.",
    ),
    (
        "Beta Inc - Onboarding Feedback", 5, "smb", CS.NEGATIVE,
        [(PPC.ONBOARDING, "Setup took two weeks longer than expected; support was slow to respond to setup questions."),
         (PPC.REPORTING, "Default dashboards don't surface the metrics our team actually tracks.")],
        ["Guided setup wizard", "Slack integration for alerts"], ["Notion"],
        ["Assign a dedicated onboarding specialist", "Follow up in 1 week to confirm setup is complete"],
        ["I nearly gave up during week one, honestly."],
        "Beta Inc had a rocky onboarding experience with slow support responses and dashboards misaligned to their needs. They're requesting a Slack integration and a guided setup flow.",
        "Onboarding took way longer than I expected, like two extra weeks longer. Every time I had a setup question support took a day or two to get back to me. And once we were finally in, the default dashboards just don't show what our team cares about day to day. We were close to giving up in the first week. A guided setup wizard would have saved us a lot of pain, and honestly a Slack integration for alerts would help too.",
    ),
    (
        "Globex - Check-in Call", 8, "enterprise", CS.MIXED,
        [(PPC.PRICING, "Seat-based pricing doesn't scale well once a team grows past 50 people."),
         (PPC.INTEGRATIONS, "No native Salesforce sync, forcing manual data entry.")],
        ["Salesforce two-way sync"], ["Salesforce", "HubSpot"],
        ["Scope a Salesforce integration proposal"],
        ["If you had Salesforce sync today, this would be an easy yes for expanding our contract."],
        "Globex likes the product but is blocked on scaling further due to seat-based pricing and the lack of a Salesforce integration, which they currently work around manually.",
        "Overall we're pretty happy, the team actually likes using it day to day. The friction is really around two things: seat-based pricing gets expensive fast once we're past fifty people, and we still don't have a real Salesforce sync so someone is manually copying data over every week. If you had Salesforce sync today, honestly this would be an easy yes for expanding our contract.",
    ),
    (
        "Initech - New Customer", 10, "startup", CS.POSITIVE,
        [(PPC.UX, "A few new team members found the initial layout slightly busy, but ramped up quickly.")],
        ["Mobile app"], [],
        [],
        ["Best onboarding experience we've had with a B2B tool, honestly."],
        "Initech is a happy new customer, praising the onboarding experience and interface, with a light request for a mobile app.",
        "This has honestly been the best onboarding experience we've had with a B2B tool. The interface is clean and our team picked it up in like a day. A couple of newer folks said the layout felt a little busy at first, but they got comfortable fast. Only real ask from us is a mobile app so people can check things on the go.",
    ),
    (
        "Umbrella Analytics - Renewal", 12, "enterprise", CS.NEGATIVE,
        [(PPC.REPORTING, "Custom report builder is too limited for advanced cross-team analysis."),
         (PPC.PERFORMANCE, "Dashboards take 8+ seconds to load once datasets get large.")],
        ["Faster dashboard load times", "Advanced custom report builder"], ["Looker"],
        ["Escalate performance ticket to engineering"],
        ["We pay for an analytics product and our own dashboards are the slowest part of our week."],
        "Umbrella is frustrated by slow dashboard performance and a limited report builder, and is evaluating Looker as an alternative for advanced analytics.",
        "Our dashboards are taking eight, sometimes ten seconds to load once we've got a full quarter of data in there. And when we try to build something more advanced than the standard report, the builder just isn't flexible enough. We pay for an analytics product and our own dashboards are the slowest part of our week. We've started looking at Looker for the more advanced stuff.",
    ),
    (
        "Hooli - Support Escalation", 14, "smb", CS.NEGATIVE,
        [(PPC.SUPPORT, "Support tickets sit unanswered for multiple days."),
         (PPC.AUTHENTICATION, "SSO intermittently logs users out mid-session.")],
        [], [],
        ["Priority support review for Hooli's account", "Engineering to investigate SSO session drops"],
        ["We pay for premium support and get radio silence."],
        "Hooli is unhappy with slow support response times and an intermittent SSO session bug, both flagged as urgent.",
        "We pay for premium support and lately we get radio silence, tickets just sit there for days. On top of that our SSO keeps logging people out in the middle of their session, which is incredibly disruptive. Both of these need to get fixed soon or this becomes a bigger conversation at renewal.",
    ),
    (
        "Stark Industries - Feature Request Call", 16, "enterprise", CS.POSITIVE,
        [(PPC.INTEGRATIONS, "Slack integration would remove a manual daily-summary step.")],
        ["Slack integration", "Webhook support for custom workflows"], [],
        ["Product to scope Slack integration timeline"],
        ["If this posted to Slack automatically, that's an hour a day back for my team."],
        "Stark Industries is a satisfied customer requesting a Slack integration and webhook support to automate a manual reporting step.",
        "Things are going well overall. The one thing that would make a real difference is a Slack integration, right now someone on my team manually copies a daily summary into our team channel. If this posted to Slack automatically, that's an hour a day back for my team. Webhook support would also open up some workflows we'd like to automate.",
    ),
    (
        "Wayne Enterprises - Mid-Contract Check-in", 18, "enterprise", CS.NEUTRAL,
        [(PPC.DOCUMENTATION, "API docs are missing examples for less common endpoints.")],
        ["More API documentation examples"], [],
        [],
        [],
        "Wayne Enterprises is a stable, neutral customer with a minor request for improved API documentation coverage.",
        "No major complaints from our side. The product does what we need. One small thing - the API docs could use more examples, especially for the less common endpoints, our engineers had to guess at the request shape a couple of times. Otherwise things are steady.",
    ),
    (
        "Pied Piper - Trial Feedback", 20, "startup", CS.MIXED,
        [(PPC.PRICING, "Trial-to-paid pricing jump feels steep for an early-stage startup."),
         (PPC.UX, "Filter controls in the interview list are hard to discover.")],
        ["Cheaper starter tier for small teams"], ["Notion"],
        [],
        ["We love the product, we just can't justify the jump from trial pricing yet."],
        "Pied Piper likes the product but finds the jump from trial to paid pricing difficult to justify at their stage, and is currently using Notion as a stopgap.",
        "We really like what this does, it's honestly better than what we've cobbled together in Notion. The problem is purely pricing, the jump from the trial to the paid plan is steep for where we are right now as an early-stage startup. A cheaper starter tier for small teams would probably close the deal for us. Also, small thing, the filter controls on the interview list took us a while to find.",
    ),
    (
        "Dunder Mifflin - Quarterly Business Review", 22, "smb", CS.POSITIVE,
        [(PPC.ANALYTICS, "Would like deeper cohort analysis in the sentiment trends view.")],
        ["Cohort-based sentiment analysis"], [],
        [],
        ["This has genuinely changed how we run our customer calls."],
        "Dunder Mifflin is a highly satisfied customer, requesting deeper cohort-level analytics on top of the existing sentiment trends.",
        "Honestly this has genuinely changed how we run our customer calls, we catch patterns we used to miss completely. If I could ask for one thing, it'd be the ability to break the sentiment trends down by customer cohort, like enterprise versus SMB, rather than just the whole book of business at once.",
    ),
    (
        "Massive Dynamic - Security Review", 24, "enterprise", CS.NEUTRAL,
        [(PPC.SECURITY, "Security team wants SOC 2 report and more granular audit logs before expanding usage.")],
        ["Granular audit logs", "SOC 2 report access"], [],
        ["Share latest SOC 2 report with Massive Dynamic's security team"],
        [],
        "Massive Dynamic is neutral on the product itself but is gating further rollout behind security requirements: SOC 2 documentation and finer-grained audit logging.",
        "The product itself is fine, no complaints there. Our blocker right now is entirely on the security side - our team wants to see the current SOC 2 report and we'd like more granular audit logs before we expand this beyond the pilot team. Once that's sorted we're likely to roll it out wider.",
    ),
    (
        "Soylent Corp - Collaboration Feedback", 26, "smb", CS.NEGATIVE,
        [(PPC.COLLABORATION, "No way to leave comments or assign follow-ups to teammates on a specific interview.")],
        ["Comment threads on interviews", "Assign action items to teammates"], ["Asana"],
        [],
        ["Right now we're pasting links into Asana just to assign follow-ups."],
        "Soylent Corp finds the lack of in-app collaboration features (comments, assignment) a real gap and is bridging it with Asana today.",
        "The insights themselves are great, but there's no way to actually collaborate around them - no comments, no way to assign a follow-up to a teammate. Right now we're pasting links into Asana just to assign follow-ups to the right person, which is a clunky extra step every time.",
    ),
    (
        "Gringotts Financial - Pricing Negotiation", 28, "enterprise", CS.NEGATIVE,
        [(PPC.PRICING, "Enterprise pricing doesn't account for seasonal usage spikes."),
         (PPC.REPORTING, "Finance wants exportable, auditable reports, not just dashboards.")],
        ["Exportable audit-ready reports"], ["Salesforce"],
        ["Prepare a usage-based pricing proposal"],
        ["We're not against paying more, we're against paying a flat rate for usage that isn't flat."],
        "Gringotts wants pricing that reflects their seasonal usage pattern and reporting that satisfies finance's audit requirements, and is weighing Salesforce as an alternative.",
        "Our usage is seasonal, it spikes hard for about six weeks a year, and the current pricing doesn't account for that at all. We're not against paying more, we're against paying a flat rate for usage that isn't flat. Separately, finance needs exportable, auditable reports, not just dashboards, for their own reviews. We have looked at Salesforce as an alternative but haven't made a decision.",
    ),
    (
        "Aperture Science - Onboarding Success", 30, "startup", CS.POSITIVE,
        [(PPC.ONBOARDING, "One early hiccup connecting their audio storage, resolved same day by support.")],
        [], [],
        [],
        ["Support fixed our setup issue same-day, which honestly surprised us."],
        "Aperture Science had a minor onboarding hiccup that support resolved quickly, leaving them satisfied overall.",
        "We hit one snag connecting our audio storage during setup, but support fixed it same-day, which honestly surprised us given how these things usually go. Since then it's been smooth. No real complaints.",
    ),
    (
        "Cyberdyne Systems - Integration Deep Dive", 33, "enterprise", CS.MIXED,
        [(PPC.INTEGRATIONS, "Zapier support exists but lacks triggers for key events like 'interview completed'.")],
        ["More granular Zapier triggers"], ["HubSpot"],
        ["Product to review Zapier trigger coverage"],
        [],
        "Cyberdyne appreciates existing Zapier support but needs more granular triggers to fully automate their workflow, and mentioned HubSpot's integration depth as a comparison point.",
        "We're using the Zapier integration already, which is good, but it's missing triggers for some key events, like when an interview finishes processing. HubSpot's integrations go a bit deeper in that respect. If Zapier support covered more granular events here, we could fully automate our downstream workflow.",
    ),
    (
        "Oscorp - Notes Upload Trial", 35, "individual", CS.NEUTRAL,
        [(PPC.UX, "As a solo user, some enterprise-oriented UI (team management, roles) feels unnecessary clutter.")],
        ["Simplified solo-user mode"], [],
        [],
        [],
        "A solo researcher trying the product finds it functional but oriented toward team usage, with some unnecessary UI for individual use cases.",
        "It works fine for what I need, mostly just uploading my own research notes and searching across them later. Some of the interface is clearly built for teams, like the roles and permissions stuff, which I just don't need as a single user. A simplified mode for individuals would be nice but it's not a dealbreaker.",
    ),
    (
        "Wonka Industries - Sentiment Deep Dive", 38, "smb", CS.POSITIVE,
        [(PPC.REPORTING, "Would like sentiment trends broken out by product line, not just overall.")],
        ["Per-product sentiment breakdown"], ["Slack"],
        [],
        ["We replaced a Slack channel full of screenshots with this, it's so much better."],
        "Wonka Industries is happy with the product, having replaced an informal Slack-based process, and wants sentiment trends segmented by product line.",
        "Before this we basically had a Slack channel full of screenshots and vibes about how customers felt. This is so much better, it's actually structured. The one thing I'd want next is being able to break the sentiment trends out by product line instead of just one big number.",
    ),
    (
        "Genco Pura - Competitive Displacement", 40, "enterprise", CS.NEGATIVE,
        [(PPC.PRICING, "Considering a switch to a cheaper competitor given budget cuts this year.")],
        [], ["Notion", "Slack"],
        ["Schedule a retention call with Genco Pura"],
        ["Budget got cut and we have to justify every tool line by line now."],
        "Genco Pura is at risk of churning due to budget pressure and is evaluating cheaper alternatives like Notion and Slack-based workflows.",
        "Our budget got cut this year and we have to justify every tool line by line now. Realistically we're looking at whether we could just make do with Notion or a Slack-based process instead, even if it's worse, just because it's free. I don't want to lose this tool, but I need to be able to make the cost case internally.",
    ),
    (
        "Bluth Company - First Impressions", 43, "smb", CS.NEUTRAL,
        [(PPC.ONBOARDING, "Getting the whole team to actually start using it took longer than expected.")],
        [], [],
        [],
        [],
        "Bluth Company is a newer customer with a slow team-wide adoption curve, but no strong complaints about the product itself.",
        "The product itself seems fine so far. The bigger challenge has just been getting the whole team to actually start using it day to day, adoption has been slower than we expected. Nothing specifically wrong with the tool, more of a change-management thing on our end.",
    ),
]

# A few interviews left in earlier pipeline states, so status filters/badges
# on the Explorer and Recent Interviews have real variety to show, not just
# "completed" everywhere.
IN_FLIGHT_INTERVIEWS = [
    ("Prestige Worldwide - Intro Call", InterviewStatus.PROCESSING, None),
    ("Vandelay Industries - Follow-up", InterviewStatus.UPLOADED, None),
    ("Sterling Cooper - Renewal Notes", InterviewStatus.FAILED, "Transcription provider returned an empty transcript."),
]


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Interview).count()
        if existing > 0:
            print(f"Database already has {existing} interview(s); refusing to double-seed. "
                  f"Delete existing rows first if you want a clean reseed.")
            return

        now = datetime.now(timezone.utc)

        for (
            title, days_ago, customer_type, sentiment, pain_points,
            feature_requests, competitors, action_items, notable_quotes,
            summary, transcript_text,
        ) in COMPLETED_INTERVIEWS:
            created_at = now - timedelta(days=days_ago, hours=days_ago % 5)
            interview = Interview(
                id=uuid.uuid4(),
                title=title,
                status=InterviewStatus.COMPLETED,
                input_type=InputType.NOTES,
                raw_notes_text=transcript_text,
                created_at=created_at,
                updated_at=created_at,
            )
            interview.transcript = Transcript(
                raw_text=transcript_text, created_at=created_at, updated_at=created_at
            )
            interview.insight = Insight(
                summary=summary,
                feature_requests=feature_requests,
                competitors=competitors,
                customer_sentiment=sentiment,
                customer_type=customer_type,
                action_items=action_items,
                notable_quotes=notable_quotes,
                created_at=created_at,
                updated_at=created_at,
                pain_points=[
                    PainPoint(category=category, description=description, created_at=created_at)
                    for category, description in pain_points
                ],
            )
            interview.embedding = Embedding(
                vector=_deterministic_unit_vector(transcript_text, 1536),
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(interview)

        for title, status, failure_reason in IN_FLIGHT_INTERVIEWS:
            created_at = now - timedelta(hours=2)
            interview = Interview(
                id=uuid.uuid4(),
                title=title,
                status=status,
                input_type=InputType.NOTES,
                raw_notes_text="Pending processing.",
                failure_reason=failure_reason,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(interview)

        db.commit()
        print(
            f"Seeded {len(COMPLETED_INTERVIEWS)} completed interviews and "
            f"{len(IN_FLIGHT_INTERVIEWS)} in-flight interviews."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
