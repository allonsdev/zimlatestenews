"""
Management command: seed_data
Usage:  python manage.py seed_data
        python manage.py seed_data --articles 40
        python manage.py seed_data --flush     (wipe first, then seed)

Creates:
  - Categories (Politics, Sport, Business, Health, Tech, Entertainment, World, Education)
  - 1 superuser + 4 Authors
  - 50 published Articles (spread across categories & priorities)
  - Comments on some articles
  - Ticker items
  - Newsletter subscribers
"""

import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Realistic sample data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"name": "Politics",      "slug": "politics",      "color": "navy",   "icon": "ti-building-government", "nav_order": 1},
    {"name": "Sport",         "slug": "sport",         "color": "green",  "icon": "ti-ball-football",        "nav_order": 2},
    {"name": "Business",      "slug": "business",      "color": "gold",   "icon": "ti-chart-bar",            "nav_order": 3},
    {"name": "Health",        "slug": "health",        "color": "teal",   "icon": "ti-heart-rate-monitor",   "nav_order": 4},
    {"name": "Technology",    "slug": "technology",    "color": "purple", "icon": "ti-device-laptop",        "nav_order": 5},
    {"name": "Entertainment", "slug": "entertainment", "color": "pink",   "icon": "ti-music",                "nav_order": 6},
    {"name": "World",         "slug": "world",         "color": "red",    "icon": "ti-world",                "nav_order": 7},
    {"name": "Education",     "slug": "education",     "color": "orange", "icon": "ti-school",               "nav_order": 8},
]

AUTHORS = [
    {"full_name": "Tendai Moyo",     "title": "Senior Political Reporter"},
    {"full_name": "Rudo Chikwanda",  "title": "Sports Editor"},
    {"full_name": "Farai Mutasa",    "title": "Business Correspondent"},
    {"full_name": "Nyasha Dube",     "title": "Health & Lifestyle Writer"},
]

ARTICLE_TEMPLATES = [
    # Politics
    {
        "title": "President Announces New Economic Recovery Plan",
        "excerpt": "The Head of State unveiled a sweeping economic recovery blueprint aimed at reducing unemployment and attracting foreign investment over the next five years.",
        "body": "<p>In a nationally televised address from State House, the President outlined a comprehensive economic recovery strategy that economists say could reshape Zimbabwe's financial landscape.</p><p>The plan includes targeted investment in agriculture, mining, and manufacturing, with special economic zones earmarked for Bulawayo and Mutare.</p><p>Opposition leaders have welcomed the initiative but called for transparency in implementation, citing past policy failures.</p><p>The World Bank and IMF have both expressed cautious optimism, with senior officials noting the plan's alignment with international best practices.</p>",
        "category": "politics", "priority": "featured",
    },
    {
        "title": "Cabinet Reshuffle: Three Ministers Replaced",
        "excerpt": "A surprise cabinet reshuffle saw three senior ministers replaced in what analysts describe as a move to energise the government's second-term agenda.",
        "body": "<p>The Office of the President confirmed the changes late Tuesday evening, with new appointments taking effect immediately.</p><p>The ministries of Finance, Health, and Home Affairs all saw leadership changes, sparking widespread debate among political commentators.</p><p>The outgoing Finance Minister said he left office 'with his head held high', pointing to a stabilised exchange rate as his legacy.</p>",
        "category": "politics", "priority": "breaking",
    },
    {
        "title": "Parliament Passes Landmark Land Reform Amendment",
        "excerpt": "Legislators approved changes to the land tenure system that could affect thousands of smallholder farmers across the country.",
        "body": "<p>The Land Reform Amendment Bill passed its third reading with 152 votes in favour and 43 against, following three weeks of heated debate.</p><p>Farmers' unions have described the legislation as 'long overdue', while critics warn of unintended consequences for commercial agriculture.</p>",
        "category": "politics", "priority": "normal",
    },
    {
        "title": "Local Elections Set for October — ZEC Confirms",
        "excerpt": "The Zimbabwe Electoral Commission has gazetted October 15 as the date for urban council elections in 32 municipalities.",
        "body": "<p>Voter registration centres will open next month, with the ZEC urging all eligible citizens to ensure they are registered ahead of the deadline.</p><p>Political parties have already begun canvassing, with the capital Harare seen as the key battleground.</p>",
        "category": "politics", "priority": "normal",
    },
    # Sport
    {
        "title": "Warriors Qualify for AFCON After Thrilling Win Over Zambia",
        "excerpt": "Zimbabwe's national football team secured their place at the Africa Cup of Nations with a dramatic 2-1 victory in Lusaka.",
        "body": "<p>Goals from Knowledge Musona and Tino Kadewere sealed a historic qualification, sending thousands of fans into celebrations across Harare and Bulawayo.</p><p>Coach Jairos Tapera praised the team's resilience after going a goal down in the first half.</p><p>'These boys showed the heart of lions tonight,' he said in his post-match press conference.</p>",
        "category": "sport", "priority": "breaking",
    },
    {
        "title": "Dynamos FC Sign Three New Players Ahead of Castle Lager Premier League",
        "excerpt": "The Harare giants have bolstered their squad with signings from South Africa and Zambia as they eye a return to domestic dominance.",
        "body": "<p>The club confirmed the signings of a striker, a central midfielder, and a goalkeeper on three-year contracts, with the transfer fees undisclosed.</p><p>Fans have reacted with excitement on social media, many believing this is the year Dynamos reclaim the league title they last won in 2021.</p>",
        "category": "sport", "priority": "featured",
    },
    {
        "title": "Zimbabwe Cricket Team Wins First ODI Against Pakistan",
        "excerpt": "In a stunning upset, the Chevrons beat Pakistan by 34 runs in the opening match of the three-game series.",
        "body": "<p>Sean Williams' century and a disciplined bowling performance were the highlights as Zimbabwe recorded one of their most celebrated victories in recent years.</p><p>Pakistan captain Babar Azam conceded his team had been outplayed, promising a stronger showing in the second ODI.</p>",
        "category": "sport", "priority": "normal",
    },
    {
        "title": "Kirsty Coventry Opens New Olympic Training Facility in Harare",
        "excerpt": "The Sports Minister officially opened a state-of-the-art sports complex designed to nurture the next generation of Zimbabwean Olympians.",
        "body": "<p>The facility, funded through a public-private partnership, includes an Olympic-standard swimming pool, athletics track, and gymnasium.</p><p>'This is just the beginning,' Minister Coventry said. 'We want Zimbabwe back on the Olympic podium.'</p>",
        "category": "sport", "priority": "normal",
    },
    # Business
    {
        "title": "ZSE Records Best Quarter in Five Years as Investor Confidence Returns",
        "excerpt": "The Zimbabwe Stock Exchange's main index gained 18% in the quarter as foreign investors returned to emerging market equities.",
        "body": "<p>Analysts attribute the rally to improved macroeconomic stability, a more predictable exchange rate regime, and rising commodity prices.</p><p>Banking stocks led the gains, with CBZ Holdings and First Capital Bank both hitting multi-year highs.</p>",
        "category": "business", "priority": "featured",
    },
    {
        "title": "Econet Wireless Launches 5G Pilot in Harare CBD",
        "excerpt": "Zimbabwe's largest telecoms company activated its first 5G base stations in the capital, promising speeds of up to 1Gbps.",
        "body": "<p>The rollout, initially covering the Harare central business district and Sam Levy's Village, is expected to reach Bulawayo by year-end.</p><p>CEO Douglas Mboweni said the investment underscores Econet's commitment to connecting Zimbabwe to the digital future.</p>",
        "category": "business", "priority": "normal",
    },
    {
        "title": "Government Cuts Fuel Import Duties to Ease Pump Prices",
        "excerpt": "Treasury has reduced import duties on petroleum products in a bid to ease the burden on consumers amid rising global oil prices.",
        "body": "<p>The measure, effective from next month, is expected to reduce the pump price of petrol by approximately $0.08 per litre.</p><p>Transport operators welcomed the announcement, while economists cautioned that the relief would be short-lived if global oil prices continue to rise.</p>",
        "category": "business", "priority": "normal",
    },
    # Health
    {
        "title": "Ministry of Health Launches Nationwide Malaria Vaccination Drive",
        "excerpt": "A mass vaccination programme targeting children under five will reach all ten provinces over the next three months.",
        "body": "<p>The campaign, supported by Gavi and the WHO, will deploy 2,000 community health workers to administer the RTS,S malaria vaccine.</p><p>Zimbabwe recorded over 1.2 million malaria cases last year, with Manicaland and Mashonaland East among the worst-affected provinces.</p>",
        "category": "health", "priority": "featured",
    },
    {
        "title": "New Parirenyatwa Hospital Wing Opens, Adding 200 Beds",
        "excerpt": "The expanded oncology and maternity wing at Zimbabwe's largest public hospital is now operational after two years of construction.",
        "body": "<p>The $14 million facility was funded through a combination of government budget allocation and a grant from the African Development Bank.</p><p>Health Minister Dr Douglas Mombeshora described the opening as 'a milestone for public healthcare in Zimbabwe'.</p>",
        "category": "health", "priority": "normal",
    },
    # Technology
    {
        "title": "Zimbabwe's Tech Startup Scene Attracts $20M in VC Funding",
        "excerpt": "Local fintech and agritech startups secured record venture capital investment in the first half of the year, according to a new report.",
        "body": "<p>The report by Disrupt Africa highlights Zimbabwe as one of the fastest-growing startup ecosystems on the continent, alongside Kenya and Nigeria.</p><p>Harare-based payments startup PayZim led the fundraising round, securing $8 million in Series A funding.</p>",
        "category": "technology", "priority": "featured",
    },
    {
        "title": "POTRAZ to Roll Out Free Wi-Fi in All Secondary Schools",
        "excerpt": "The Postal and Telecommunications Regulatory Authority of Zimbabwe plans to connect 1,800 secondary schools to broadband internet by 2026.",
        "body": "<p>The project, part of the government's digital inclusion agenda, will use a combination of fibre, fixed wireless, and satellite connectivity.</p><p>Educators have welcomed the initiative, saying reliable internet access will transform teaching and learning across the country.</p>",
        "category": "technology", "priority": "normal",
    },
    # Entertainment
    {
        "title": "Jah Prayzah Sells Out Harare International Conference Centre",
        "excerpt": "The Zimbabwean music icon performed to a packed 5,000-seat crowd in what critics are calling his best live show yet.",
        "body": "<p>Backed by his Military Touch Movement band, Jah Prayzah delivered a two-hour set spanning his entire catalogue, from early hits to tracks from his latest album.</p><p>Special guest appearances from Winky D and Ammara Brown sent the crowd into a frenzy.</p>",
        "category": "entertainment", "priority": "normal",
    },
    {
        "title": "Zimbabwean Film 'Nhaka' Selected for Sundance Film Festival",
        "excerpt": "Director Rumbi Katedza's debut feature has earned a coveted spot at the prestigious American film festival, a first for Zimbabwean cinema.",
        "body": "<p>The film, which explores intergenerational trauma and land dispossession, was praised by Sundance selectors for its 'raw emotional power and visual poetry'.</p><p>Katedza said she hopes the film opens doors for more Zimbabwean stories to reach international audiences.</p>",
        "category": "entertainment", "priority": "featured",
    },
    # World
    {
        "title": "AU Summit Adopts New Framework on African Free Trade",
        "excerpt": "African heads of state agreed to accelerate implementation of the AfCFTA at this year's African Union summit in Addis Ababa.",
        "body": "<p>Zimbabwe's President attended the summit and signed a bilateral trade protocol with three neighbouring countries on the sidelines.</p><p>Trade ministers described the meeting as 'the most productive AU summit in a decade' on trade matters.</p>",
        "category": "world", "priority": "normal",
    },
    {
        "title": "UN Security Council Discusses Sudan Crisis — Africa Bloc Pushes for Ceasefire",
        "excerpt": "African nations on the UN Security Council presented a joint resolution calling for an immediate ceasefire in the Sudanese civil war.",
        "body": "<p>Zimbabwe's ambassador to the UN co-signed the resolution, which has garnered support from 11 of the 15 Security Council members.</p><p>Aid agencies warn that over 8 million people face acute food insecurity as the conflict enters its second year.</p>",
        "category": "world", "priority": "normal",
    },
    # Education
    {
        "title": "University of Zimbabwe Ranks Among Top 10 African Universities",
        "excerpt": "The QS African University Rankings placed UZ at number 8 on the continent, up from 14 last year, citing research output improvements.",
        "body": "<p>The university's engineering and medical faculties were singled out for particular praise in the rankings methodology.</p><p>Vice-Chancellor Professor Paul Mapfumo said the ranking reflects 'years of investment in academic infrastructure and faculty development'.</p>",
        "category": "education", "priority": "featured",
    },
    {
        "title": "Government Increases Teacher Salaries by 40% Following Strike Threat",
        "excerpt": "The Public Service Commission announced the pay rise after weeks of negotiations with the Zimbabwe Teachers' Association.",
        "body": "<p>The increase will be backdated to the beginning of the school term, with arrears to be paid out within 60 days.</p><p>ZIMTA president Robson Chere said members would return to work immediately, averting a nationwide teachers' strike that threatened to disrupt examinations.</p>",
        "category": "education", "priority": "breaking",
    },
]

TICKER_ITEMS = [
    {"text": "BREAKING: Warriors qualify for AFCON 2025 after 2-1 win over Zambia", "url": ""},
    {"text": "ZSE main index gains 18% in best quarter since 2019", "url": ""},
    {"text": "President to address the nation at 8PM tonight on state broadcaster ZBC", "url": ""},
    {"text": "Parirenyatwa Hospital new wing now open — 200 additional beds available", "url": ""},
    {"text": "Econet activates first 5G base stations in Harare CBD", "url": ""},
]

COMMENTS = [
    ("Chiedza Maposa", "chiedza@example.com", "Great reporting, this is exactly the kind of in-depth coverage we need."),
    ("Blessing Ncube", "blessing@example.com", "I have mixed feelings about this. The implementation details are still very vague."),
    ("Tapiwa Gweru", "tapiwa@example.com", "Finally some good news! Zimbabwe is moving forward."),
    ("Simba Mutare", "simba@example.com", "This needs more scrutiny. We've heard these promises before."),
    ("Faith Zhakata", "faith@example.com", "Very informative article, thank you ZimLatestNews."),
]


class Command(BaseCommand):
    help = "Seed the database with sample ZimLatestNews data"

    def add_arguments(self, parser):
        parser.add_argument("--articles", type=int, default=len(ARTICLE_TEMPLATES),
                            help="Number of articles to create (default: all templates)")
        parser.add_argument("--flush", action="store_true",
                            help="Delete existing seeded data before seeding")

    def handle(self, *args, **options):
        if options["flush"]:
            self.flush_data()

        self.stdout.write(self.style.MIGRATE_HEADING("=== ZimLatestNews Seeder ==="))

        categories  = self.seed_categories()
        authors     = self.seed_authors()
        articles    = self.seed_articles(categories, authors, options["articles"])
        self.seed_comments(articles)
        self.seed_ticker()
        self.seed_subscribers()

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Done — {len(categories)} categories, {len(authors)} authors, "
            f"{len(articles)} articles seeded."
        ))

    # ------------------------------------------------------------------
    def flush_data(self):
        from categories.models import Category
        from articles.models import Article, Author, Comment
        from pages.models import TickerItem, NewsletterSubscriber

        self.stdout.write("  Flushing existing data…")
        Comment.objects.all().delete()
        Article.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()
        TickerItem.objects.all().delete()
        NewsletterSubscriber.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("  Flushed."))

    # ------------------------------------------------------------------
    def seed_categories(self):
        from categories.models import Category

        self.stdout.write("\n  Creating categories…")
        cats = {}
        for data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name":        data["name"],
                    "color":       data["color"],
                    "icon":        data["icon"],
                    "nav_order":   data["nav_order"],
                    "show_in_nav": True,
                    "is_active":   True,
                    "description": f"Latest {data['name']} news from Zimbabwe and beyond.",
                    "seo_title":   f"{data['name']} News — ZimLatestNews",
                    "seo_description": f"Read the latest {data['name'].lower()} news, analysis and opinion from ZimLatestNews.",
                }
            )
            cats[data["slug"]] = cat
            status = "created" if created else "exists"
            self.stdout.write(f"    {cat.name} [{status}]")
        return cats

    # ------------------------------------------------------------------
    def seed_authors(self):
        from articles.models import Author

        self.stdout.write("\n  Creating authors…")

        # Ensure superuser exists
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@zimlatestnews.online", "admin1234")
            self.stdout.write(self.style.WARNING("    Superuser 'admin' created (password: admin1234)"))

        authors = []
        for i, data in enumerate(AUTHORS):
            username = slugify(data["full_name"]).replace("-", "")
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@zimlatestnews.online",
                          "first_name": data["full_name"].split()[0],
                          "last_name":  data["full_name"].split()[-1]}
            )
            if not user.has_usable_password():
                user.set_password("password123")
                user.save()

            author, created = Author.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": data["full_name"],
                    "title":     data["title"],
                    "bio":       f"{data['full_name']} is a {data['title']} at ZimLatestNews, covering stories that matter to Zimbabweans.",
                    "is_active": True,
                }
            )
            authors.append(author)
            status = "created" if created else "exists"
            self.stdout.write(f"    {author.full_name} [{status}]")
        return authors

    # ------------------------------------------------------------------
    def seed_articles(self, categories, authors, count):
        from articles.models import Article

        self.stdout.write("\n  Creating articles…")
        templates = ARTICLE_TEMPLATES[:count]
        # If count > templates available, cycle through them
        if count > len(ARTICLE_TEMPLATES):
            templates = (ARTICLE_TEMPLATES * ((count // len(ARTICLE_TEMPLATES)) + 1))[:count]

        created_articles = []
        now = timezone.now()

        for i, tmpl in enumerate(templates):
            # Spread publish dates over last 30 days
            published_at = now - timedelta(hours=random.randint(1, 720))
            cat = categories.get(tmpl["category"])
            author = random.choice(authors)
            slug = slugify(tmpl["title"])

            # Ensure unique slug
            if Article.objects.filter(slug=slug).exists():
                slug = f"{slug}-{i}"

            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    "title":        tmpl["title"],
                    "subtitle":     "",
                    "excerpt":      tmpl["excerpt"],
                    "body":         tmpl["body"],
                    "author":       author,
                    "category":     cat,
                    "status":       Article.Status.PUBLISHED,
                    "priority":     tmpl.get("priority", "normal"),
                    "published_at": published_at,
                    "allow_comments": True,
                    "show_ads":     True,
                    "seo_title":    tmpl["title"],
                    "seo_description": tmpl["excerpt"][:160],
                }
            )
            created_articles.append(article)
            status = "created" if created else "exists"
            self.stdout.write(f"    [{i+1}] {article.title[:60]} [{status}]")

        return created_articles

    # ------------------------------------------------------------------
    def seed_comments(self, articles):
        from articles.models import Comment

        self.stdout.write("\n  Adding comments…")
        count = 0
        for article in random.sample(articles, min(8, len(articles))):
            for name, email, body in random.sample(COMMENTS, random.randint(1, 3)):
                Comment.objects.get_or_create(
                    article=article,
                    email=email,
                    defaults={"name": name, "body": body, "is_approved": True}
                )
                count += 1
        self.stdout.write(f"    {count} comments added.")

    # ------------------------------------------------------------------
    def seed_ticker(self):
        from pages.models import TickerItem

        self.stdout.write("\n  Creating ticker items…")
        for i, item in enumerate(TICKER_ITEMS):
            TickerItem.objects.get_or_create(
                text=item["text"],
                defaults={"url": item["url"], "is_active": True, "order": i}
            )
        self.stdout.write(f"    {len(TICKER_ITEMS)} ticker items added.")

    # ------------------------------------------------------------------
    def seed_subscribers(self):
        from pages.models import NewsletterSubscriber

        self.stdout.write("\n  Creating newsletter subscribers…")
        subscribers = [
            ("tendai.moyo@gmail.com", "Tendai Moyo"),
            ("rudo.chikwanda@outlook.com", "Rudo Chikwanda"),
            ("farai.mutasa@yahoo.com", "Farai Mutasa"),
            ("nyasha.dube@proton.me", "Nyasha Dube"),
            ("simba.mutare@gmail.com", "Simba Mutare"),
        ]
        for email, name in subscribers:
            NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={"name": name, "is_active": True, "confirmed": True}
            )
        self.stdout.write(f"    {len(subscribers)} subscribers added.")