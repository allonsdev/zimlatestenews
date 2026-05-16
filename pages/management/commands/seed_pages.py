from django.core.management.base import BaseCommand
from pages.models import Page

PAGES = [
    {
        "title": "About Us",
        "slug": "about",
        "template": Page.Template.ABOUT,
        "seo_title": "About Us | ZimLatestNews",
        "seo_description": "Learn about ZimLatestNews, Zimbabwe's most trusted independent news source since 2025.",
        "body": """
            <h2>About ZimLatestNews</h2>
            <p>ZimLatestNews is Zimbabwe's most trusted independent news source, founded in 2025.
            We are committed to delivering accurate, timely and balanced reporting on politics,
            business, sport, health, technology and entertainment.</p>

            <h3><i class="ti ti-target"></i> Our Mission</h3>
            <p>To inform, educate and empower Zimbabweans at home and in the diaspora with
            credible, fearless journalism.</p>

            <h3><i class="ti ti-users"></i> Our Team</h3>
            <p>Our newsroom is staffed by experienced journalists based in Harare, Bulawayo
            and across the country.</p>

            <h3><i class="ti ti-eye"></i> Editorial Standards</h3>
            <p>We follow strict editorial guidelines to ensure every story is verified before
            publication. Corrections are published promptly and transparently.</p>

            <h3><i class="ti ti-mail"></i> Contact the Newsroom</h3>
            <p>Email us at <a href="mailto:news@zimlatestnews.online">news@zimlatestnews.online</a>
            or visit our <a href="/pages/contact/">contact page</a>.</p>
        """,
    },
    {
        "title": "Advertise",
        "slug": "advertise",
        "template": Page.Template.ADVERTISE,
        "seo_title": "Advertise | ZimLatestNews",
        "seo_description": "Advertise with ZimLatestNews and reach Zimbabwe's most engaged digital news audience.",
        "body": """
            <h2>Advertise with ZimLatestNews</h2>
            <p>Reach Zimbabwe's most engaged digital news audience. We offer a range of
            advertising solutions to suit every budget and objective.</p>

            <h3><i class="ti ti-layout"></i> Ad Formats</h3>
            <ul>
                <li>Leaderboard (728 x 90)</li>
                <li>Medium Rectangle (300 x 250)</li>
                <li>Sponsored Articles</li>
                <li>Newsletter Placements</li>
                <li>Breaking News Banner</li>
            </ul>

            <h3><i class="ti ti-chart-bar"></i> Why Advertise with Us</h3>
            <ul>
                <li>Highly engaged Zimbabwean readership</li>
                <li>Desktop and mobile optimised placements</li>
                <li>Transparent reporting and analytics</li>
                <li>Flexible campaign durations</li>
            </ul>

            <h3><i class="ti ti-mail"></i> Get in Touch</h3>
            <p>Email us at <a href="mailto:ads@zimlatestnews.online">ads@zimlatestnews.online</a>
            or call <strong>+263 77 000 0000</strong> to request our media kit.</p>
        """,
    },
    {
        "title": "Privacy Policy",
        "slug": "privacy",
        "template": Page.Template.DEFAULT,
        "seo_title": "Privacy Policy | ZimLatestNews",
        "seo_description": "Read the ZimLatestNews privacy policy to understand how we collect and use your data.",
        "body": """
            <h2>Privacy Policy</h2>
            <p><em>Last updated: May 2025</em></p>

            <h3><i class="ti ti-database"></i> Information We Collect</h3>
            <p>We collect information you provide directly to us, such as when you subscribe
            to our newsletter, submit a contact form, or comment on an article.</p>

            <h3><i class="ti ti-settings"></i> How We Use Your Information</h3>
            <ul>
                <li>To send you our newsletter (if subscribed)</li>
                <li>To respond to your enquiries</li>
                <li>To improve our services</li>
                <li>To display relevant advertising via Google AdSense</li>
            </ul>

            <h3><i class="ti ti-cookie"></i> Cookies</h3>
            <p>We use cookies to analyse site traffic and personalise content.
            You can control cookies through your browser settings.</p>

            <h3><i class="ti ti-building"></i> Third Parties</h3>
            <p>We use Google AdSense for advertising and Google Analytics for traffic analysis.
            These services have their own privacy policies.</p>

            <h3><i class="ti ti-mail"></i> Contact</h3>
            <p>For privacy concerns email
            <a href="mailto:news@zimlatestnews.online">news@zimlatestnews.online</a>.</p>
        """,
    },
    {
        "title": "Terms of Use",
        "slug": "terms",
        "template": Page.Template.DEFAULT,
        "seo_title": "Terms of Use | ZimLatestNews",
        "seo_description": "Read the ZimLatestNews terms of use before accessing our site.",
        "body": """
            <h2>Terms of Use</h2>
            <p><em>Last updated: May 2025</em></p>

            <h3><i class="ti ti-file-check"></i> Acceptance of Terms</h3>
            <p>By accessing ZimLatestNews you agree to be bound by these terms.
            If you do not agree, please do not use our site.</p>

            <h3><i class="ti ti-copyright"></i> Content</h3>
            <p>All content published on ZimLatestNews is protected by copyright.
            You may not reproduce, distribute or republish our content without
            written permission.</p>

            <h3><i class="ti ti-user-check"></i> User Conduct</h3>
            <p>You agree not to post defamatory, abusive, or unlawful comments.
            We reserve the right to remove any content and ban users who violate
            these terms.</p>

            <h3><i class="ti ti-alert-circle"></i> Disclaimer</h3>
            <p>ZimLatestNews strives for accuracy but cannot guarantee that all
            information is error free. We are not liable for any loss arising
            from reliance on our content.</p>

            <h3><i class="ti ti-refresh"></i> Changes</h3>
            <p>We may update these terms at any time. Continued use of the site
            constitutes acceptance of the updated terms.</p>
        """,
    },
    {
        "title": "E-Paper",
        "slug": "epaper",
        "template": Page.Template.DEFAULT,
        "seo_title": "E-Paper | ZimLatestNews",
        "seo_description": "Read the ZimLatestNews digital e-paper edition on any device.",
        "body": """
            <h2>ZimLatestNews E-Paper</h2>
            <p>Read our digital edition — the full newspaper experience on any device.</p>

            <h3><i class="ti ti-device-tablet"></i> Read Anywhere</h3>
            <p>Our e-paper is updated daily and gives you access to every page of
            ZimLatestNews in a familiar newspaper layout, whether you are on a phone,
            tablet or desktop.</p>

            <h3><i class="ti ti-list-check"></i> How to Access</h3>
            <ul>
                <li>Subscribe to our newsletter to receive the daily e-paper link</li>
                <li>Follow us on social media for daily edition announcements</li>
            </ul>

            <h3><i class="ti ti-mail"></i> Subscriptions</h3>
            <p>For e-paper subscriptions email
            <a href="mailto:news@zimlatestnews.online">news@zimlatestnews.online</a>.</p>
        """,
    },
    {
        "title": "Newsletter",
        "slug": "newsletter",
        "template": Page.Template.DEFAULT,
        "seo_title": "Newsletter | ZimLatestNews",
        "seo_description": "Subscribe to the free ZimLatestNews newsletter and get Zimbabwe's top stories every morning.",
        "body": """
            <h2>ZimLatestNews Newsletter</h2>
            <p>Stay ahead of the news. Get Zimbabwe's top stories delivered free
            to your inbox every morning.</p>

            <h3><i class="ti ti-gift"></i> What You Get</h3>
            <ul>
                <li>Daily morning digest of top stories</li>
                <li>Breaking news alerts</li>
                <li>Weekly roundup every Friday</li>
                <li>No spam, unsubscribe any time</li>
            </ul>

            <h3><i class="ti ti-mail-forward"></i> How to Subscribe</h3>
            <p>Enter your email address in the form below or on our
            <a href="/">homepage</a> and click Subscribe. It is completely free.</p>
        """,
    },
]


class Command(BaseCommand):
    help = "Seed all required static pages into the database"

    def handle(self, *args, **options):
        for data in PAGES:
            page, created = Page.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title":           data["title"],
                    "body":            data["body"],
                    "template":        data["template"],
                    "seo_title":       data.get("seo_title", ""),
                    "seo_description": data.get("seo_description", ""),
                    "status":          Page.Status.PUBLISHED,
                    "show_in_footer":  True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created: {data['slug']}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Skipped (already exists): {data['slug']}"))

        self.stdout.write(self.style.SUCCESS("\nDone. All pages seeded."))