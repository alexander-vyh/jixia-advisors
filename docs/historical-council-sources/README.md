# Historical Council Sources

This README records build-time sources for the optional historical
representative lenses behind the six convening methods. These sources should
shape registry metadata, source notes, confidence labels, representative
limitations, and method-specific process rules.

They are not runtime prompt context. Historical representatives must remain
lazy, method-scoped, source-backed lenses. They should not claim to speak as the
actual people, councils, or offices named here.

## Source Use Rules

- Prefer primary texts in scholarly editions, peer-reviewed articles, academic
  monographs, and specialist reference works.
- Use open web translations as access aids, not final interpretive authorities,
  when stronger scholarly editions exist.
- Use `person` representatives only when the source tradition supports a named
  person for the intended stance. Use `role` or `exemplar` for institutions and
  unstable traditions.
- Preserve uncertainty in the registry. A source note is allowed to say that a
  tradition is late, literary, rhetorical, contested, or retrospective.
- Translate the historical source into a useful review stance. Do not turn the
  method into historical roleplay.

## Method Behavior Contracts

The six methods must differ in behavior, not only in advisor background. A valid
implementation should encode the method's entry gate, phase sequence, output
shape, and refusal condition.

> Note: once the v2 method registry exists, **the registry is the canonical
> source** for entry gates, phases, output-field sets, and refusal conditions.
> The table below is a human-readable summary derived from it; if the two ever
> diverge, the registry wins.

| Method | Use when | Required behavior | Output shape | Refuse or redirect when |
| --- | --- | --- | --- | --- |
| `jixia` | The user needs everyday counsel or a right-sized set of lenses. | Triage the question, select the smallest useful advisor mix, add a counter-lens only when it materially improves the answer, then synthesize one practical next action. | Brief diagnosis, selected lenses, tension or dissent, recommended next action. | The prompt needs formal adjudication, audit, stakeholder treaty-making, or habit-loop design more than general counsel. |
| `seven-sages` | The user wants bounded breadth on an ambiguous planning question. | Cap the active voices at seven, ask each for a compact principle or warning, compare maxims, and converge on a short synthesis. | Up to seven terse perspectives, convergence/divergence map, one distilled counsel statement. | The question needs evidence trial, source-law interpretation, operational inspection, or long coaching cadence. |
| `areopagus` | The user needs a high-stakes decision reviewed before action. | Gate jurisdiction, frame the case, classify evidence and harm, test mandate/precedent/legitimacy, then issue judgment and remedy. | Case record, admissible concerns, verdict, remedy or remand. | The ask is exploratory brainstorming or routine advice without a consequential decision to adjudicate. |
| `junto` | The user needs self-improvement, operating cadence, or civic/practical improvement. | Convert the topic into prepared queries, keep debate truth-seeking rather than victory-seeking, produce experiments, commitments, and next check-in prompts. | Query list, useful observations, experiment or habit commitment, follow-up check. | The issue needs formal ruling, red-team inspection, or stakeholder authority balancing rather than improvement practice. |
| `parishad` | The user needs tradeoffs across roles, duties, sources of authority, or stakeholders. | Identify sources of authority, affected roles, interpretive conflicts, custom/context, and the least-violating settlement. | Authority map, stakeholder/role obligations, conflict interpretation, settlement with caveats. | The ask has no real role/source conflict and only needs tactical advice or audit. |
| `yushitai` | The user needs accountability, audit, remonstrance, or failure-mode detection. | Trace inspection paths, collect evidence, identify misconduct or control gaps, test capture/retaliation risk, and recommend escalation or correction. | Findings, evidence path, accountable owner, severity, corrective action. | The ask needs open-ended ideation or balanced synthesis rather than inspection and accountability. |

Behavior checks should fail a registry where all six methods share the same
phase names or output template with only the method id changed.

## Areopagus

Configuration direction: constrained adjudicative review for consequential
decisions. Use institution, role, and exemplar representatives rather than a
fake stable membership list.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Aristotle / Aristotelian school, *Constitution of the Athenians*, trans. H. Rackham, 1935. <https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0046> | Primary constitutional treatise; high, but late fourth-century and source-layered. | Supports former-archon membership, law-guardian traditions, and Ephialtes' limitation of the Areopagus. Use with source-critical caveats. |
| 2 | Plutarch, *Life of Solon*, trans. John Dryden. <https://classics.mit.edu/Plutarch/solon.html> | Primary ancient biography; useful but late and moralizing. | Supports the Areopagus as former-archon council and law-guardian memory, while preserving uncertainty about whether Solon founded or reworked it. |
| 3 | Aeschylus, *Eumenides*, trans. H. W. Smyth, Loeb 1926. <https://www.theoi.com/Text/AeschylusEumenides.html> | Primary tragedy; strong literary evidence, weak procedural evidence. | Useful for a trial-reader lens: accusation, defense, vote, acquittal, and civic reconciliation. Do not treat as literal court procedure. |
| 4 | Demosthenes, *Against Aristocrates* 23, trans. A. T. Murray, Loeb 1930. Loeb work page: <https://www.loebclassics.com/view/demosthenes-orations_xx-xxvi/1935/pb_LCL299.ix.xml> | Primary forensic speech; strong for legal argument, but adversarial. | Supports homicide-law categories and specialized Areopagus jurisdiction. Do not treat as neutral institutional history. |
| 5 | Isocrates, *Areopagiticus* 7, trans. George Norlin, Loeb 1928. Loeb work page: <https://www.loebclassics.com/view/isocrates-discourses/1928/pb_LCL209.ix.xml> | Primary political rhetoric; useful but nostalgic. | Supports law-guardian and civic-morality memory. Should shape a review stance, not override legal-procedural sources. |
| 6 | Aristotle, *Politics* 2.12, 1273b-1274a. Loeb work page: <https://www.loebclassics.com/view/aristotle-politics/1932/pb_LCL264.ix.xml> | Primary political theory; high-level and schematic. | Supports mixed-constitution balance: elite review remains constrained by popular courts and assembly. |
| 7 | Robert W. Wallace, *The Areopagos Council, to 307 B.C.*, Johns Hopkins University Press, 1989. ISBN `9780801837536`. | Academic monograph; highest-priority specialist study. | Best anchor for institutional history, uncertain origins, shifting powers, and role/exemplar treatment. |
| 8 | T. E. Rihll, "Democracy Denied: Why Ephialtes Attacked the Areiopagus," *Journal of Hellenic Studies* 115 (1995), 87-98. <https://doi.org/10.2307/631645> | Peer-reviewed article; high. | Supports an Ephialtean power-limiter lens focused on mandate control and accountability. |
| 9 | P. J. Rhodes, *A Commentary on the Aristotelian Athenaion Politeia*, Oxford University Press, 1981; rev. 1993. ISBN `9780198149427`. | Academic commentary; very high. | Use for source criticism around Solonian claims, the "Areopagite constitution," and Ephialtes. |
| 10 | Douglas M. MacDowell, *Athenian Homicide Law in the Age of the Orators*, Manchester University Press, 1963. | Academic monograph; classic specialist legal study. | Anchors Areopagus as a specialized homicide court and prevents generic review-board drift. |
| 11 | Michael Gagarin, *Drakon and Early Athenian Homicide Law*, Yale University Press, 1981. ISBN `9780300026165`. | Academic monograph; high. | Separates Draconian homicide-law foundations from later Solonian constitutional memory. |
| 12 | David D. Phillips, "Areopagus," *Oxford Classical Dictionary*, Oxford University Press, 2010. <https://doi.org/10.1093/acrefore/9780199381135.013.795> | Specialist reference; high as orientation. | Good concise source note for origin, function, and later transformation. Do not rely on it alone. |
| 13 | Robert W. Wallace, "Ephialtes and the Areopagus," *Greek, Roman, and Byzantine Studies* 15 (1974), 259-269. | Academic article; high. | Useful secondary support for the power-limiter exemplar and uncertainty around Ephialtes' motives and effects. |
| 14 | Matteo Zaccarini, "The Fate of the Lawgiver: The Invention of the Reforms of Ephialtes and the 'Patrios Politeia,'" *Historia* 67.4 (2018), 495-512. <https://www.jstor.org/stable/45019304> | Peer-reviewed article; high. | Helps keep "Ephialtean reforms" notes source-critical rather than treating later traditions as clean fact. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `former-archon-councillor` | `role` | high | Source-grounded as an ex-archon membership pattern, not a named person or guaranteed expertise. |
| `areopagite-homicide-juror` | `role` | high | Jurisdiction-specific; should not become a generic architecture-review persona. |
| `solonian-law-guardian` | `role` | medium | Use as a law-guardian tradition; do not claim Solon founded the Areopagus. |
| `ephialtean-power-limiter` | `exemplar` | medium-high | Not an Areopagus member; represents democratic correction and jurisdiction control. |
| `aeschylean-trial-reader` | `exemplar` | medium | Literary/mythic source; useful for process symbolism, not literal procedure. |
| `draconian-homicide-law-keeper` | `role` | medium-high | Useful only when the decision resembles grave harm classification. |

## Jixia

Configuration direction: adaptive pluralist counsel near power. Use source-backed
scholars and school lenses as optional representatives, but keep the default
method practical and lightweight.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Sima Qian, *Records of the Grand Historian* / *Shiji*, especially traditions around Mencius, Xun Qing, Zou Yan, Shen Dao, Tian Pian, and Qi patronage. English scholarly locator: *The Grand Scribe's Records*, ed. William H. Nienhauser Jr., Indiana University Press. | Primary historical tradition; indispensable but Han retrospective. | Anchors the academy tradition and associated scholars. Treat named rosters as transmitted memory, not institutional minutes. |
| 2 | *Mencius*, trans. D. C. Lau, Penguin, 1970; or Bryan W. Van Norden, Hackett, 2008. | Primary philosophical text in scholarly translation; high. | Supports ruler-advisor dialogue with King Xuan of Qi and moral-political remonstrance. |
| 3 | *Xunzi: The Complete Text*, trans. Eric L. Hutton, Princeton University Press, 2014. <https://press.princeton.edu/books/paperback/9780691169316/xunzi> | Primary philosophical text in modern scholarly translation; high. | Supports debate, critique of rival schools, ritual/order stance, and Xunzi's Jixia association. |
| 4 | John Knoblock, *Xunzi: A Translation and Study of the Complete Works*, Stanford University Press, 1988-1994. | Primary translation plus academic study; high. | Use for Xunzi chronology, Jixia context, and source-critical biographical claims. |
| 5 | Paul R. Goldin, "Xunzi," *Stanford Encyclopedia of Philosophy*, 2018. <https://plato.stanford.edu/entries/xunzi/> | Specialist reference; high. | Concise source for Xunzi's role, reception, and limits of biographical certainty. |
| 6 | Masayuki Sato, *The Confucian Quest for Order: The Origin and Formation of the Political Thought of Xun Zi*, Brill, 2003. | Academic monograph; high. | Strong source for Xunzi's political thought and Warring States institutional context. |
| 7 | Randall P. Peerenboom, *Law and Morality in Ancient China: The Silk Manuscripts of Huang-Lao*, SUNY Press, 1993. | Academic monograph; high. | Supports Huang-Lao governance synthesis and the Jixia-adjacent legal/moral blend. |
| 8 | W. Allyn Rickett, *Guanzi: Political, Economic, and Philosophical Essays from Early China*, Princeton University Press, 1998/2001. | Scholarly translation/study; high. | Use for Guanzi/Jixia-linked policy, economics, self-cultivation, and syncretic statecraft. |
| 9 | John Makeham, *Name and Actuality in Early Chinese Thought*, SUNY Press, 1994. | Academic monograph; high. | Supports Yin Wen/name-and-actuality lens and Warring States semantic governance concerns. |
| 10 | Eirik Lang Harris, *The Shenzi Fragments: A Philosophical Analysis and Translation*, Columbia University Press, 2016. | Scholarly translation/study; high. | Supports a Shen Dao positional-authority lens with explicit fragmentary-source limits. |
| 11 | Michael Loewe and Edward L. Shaughnessy, eds., *The Cambridge History of Ancient China: From the Origins of Civilization to 221 B.C.*, Cambridge University Press, 1999. | Academic synthesis; high. | Use for Qi/Linzi/Warring States background and cautious institutional framing. |
| 12 | A. C. Graham, *Disputers of the Tao: Philosophical Argument in Ancient China*, Open Court, 1989. | Academic synthesis; high. | Supports plural debate across early Chinese schools; useful for multi-lens method shape. |
| 13 | Harold D. Roth, *Original Tao: Inward Training (Nei-yeh) and the Foundations of Taoist Mysticism*, Columbia University Press, 1999. | Scholarly translation/study; high. | Supports Guanzi/Neiye self-cultivation lens while keeping dating and attribution cautious. |
| 14 | Mark Csikszentmihalyi and Philip J. Ivanhoe, eds., *Religious and Philosophical Aspects of the Laozi*, SUNY Press, 1999. | Academic edited volume; high. | Useful for Huang-Lao / early Daoist context, not as direct Jixia membership evidence. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `mencius-remonstrator` | `person` | high | Strong named textual tradition, but not a default moral trump card for every issue. |
| `xunzi-ritual-orderer` | `person` | high | Strong textual base; Jixia biographical details still require source caveats. |
| `zou-yan-correlative-systematizer` | `person` | medium | Major associated figure, but writings are lost and later reports dominate. |
| `shen-dao-positional-authority` | `person` | medium-high | Fragmentary text; use for authority/position analysis, not full-system confidence. |
| `yin-wen-name-actuality` | `person` | medium | Thin and contested evidence; useful as semantic-governance lens. |
| `song-xing-anti-conflict` | `person` | medium | Later reports and rival critiques dominate; use cautiously. |
| `chunyu-kun-court-wit` | `person` | medium | Useful for rhetorical counsel near power; anecdotal tradition is strong. |
| `huang-lao-synthesizer` | `role` | medium-high | Better as a school/role lens than a named person. |

## Junto

Configuration direction: mutual improvement through prepared queries,
disciplined debate, member aid, civic projects, and practical artifacts.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Benjamin Franklin, *The Autobiography of Benjamin Franklin*, written 1771-1790; Bigelow/Pine ed. 1916. <https://www.gutenberg.org/files/20203/20203-h/20203-h.htm> | Primary memoir; essential but retrospective. | Source for founding, Friday meetings, rotating queries, quarterly essays, debate discipline, and member sketches. |
| 2 | *The Papers of Benjamin Franklin, Digital Edition*, ed. Leonard W. Labaree et al., Yale/APS. <https://franklinpapers.org/> | Scholarly primary edition; highest authority. | Prefer over unsourced retellings for canonical text, dates, and editorial notes. |
| 3 | *Benjamin Franklin Papers*, Library of Congress. <https://www.loc.gov/collections/benjamin-franklin-papers/about-this-collection/> | Archival collection/finding aid; high. | Manuscript provenance and broader correspondence context. |
| 4 | Benjamin Franklin, *Political, Miscellaneous, and Philosophical Pieces*, ed. Benjamin Vaughan, 1779, pp. 533-536. Franklin Papers locator: <http://franklinpapers.org/framedVolumes.jsp?vol=1&page=255a> | Early printed primary/near-primary edition; strong. | Contains the Junto question list and admission questions. Use as prompt-bank model. |
| 5 | *The Papers of Benjamin Franklin, Vol. 1: January 6, 1706 through December 31, 1734*, ed. Leonard W. Labaree, Yale University Press, 1959. <https://yalebooks.yale.edu/book/9780300006506/the-papers-of-benjamin-franklin-vol-1/> | Scholarly edited primary volume; highest. | Best citation target for early Junto-era documents and commentary. |
| 6 | *Benjamin Franklin's Autobiography: A Norton Critical Edition*, ed. J. A. Leo Lemay and P. M. Zall, 1986. <https://wwnorton.com/books/9780393952940> | Critical edition; strong. | Use to flag publication history and memoir limits. |
| 7 | J. A. Leo Lemay, *The Life of Benjamin Franklin, Vol. 1: Journalist, 1706-1730*, University of Pennsylvania Press, 2006. <https://www.upenn.edu/pennpress/book/14258.html> | Academic biography; high. | Best secondary source for Franklin before and during Junto formation. |
| 8 | J. A. Leo Lemay, *The Life of Benjamin Franklin, Vol. 2: Printer and Publisher, 1730-1747*, University of Pennsylvania Press, 2006. <https://www.upenn.edu/pennpress/book/14259.html> | Academic biography; high. | Use for Junto-to-civic-project pipeline. |
| 9 | Alan Craig Houston, *Benjamin Franklin and the Politics of Improvement*, Yale University Press, 2008/2009. <https://yalebooks.yale.edu/book/9780300152395/benjamin-franklin-and-the-politics-of-improvement/> | Academic monograph; high. | Frames improvement as civic, moral, economic, and institutional practice. |
| 10 | H. W. Brands, *The First American: The Life and Times of Benjamin Franklin*, 2000. <https://www.penguinrandomhouse.com/books/18135/the-first-american-by-h-w-brands/> | Scholarly trade biography; reputable synthesis. | Accessible background on Junto, Library Company, and civic entrepreneurship. |
| 11 | Walter Isaacson, *Benjamin Franklin: An American Life*, 2003. <https://www.simonandschuster.com/books/Benjamin-Franklin/Walter-Isaacson/9780743258074> | Scholarly trade biography; reputable synthesis. | Good readable explanation of Junto as social network plus improvement engine. |
| 12 | Carl Van Doren, *Benjamin Franklin*, 1938. <https://archive.org/details/benjaminfranklin00vand> | Pulitzer-winning biography; classic, dated. | Useful comparative interpretation; cross-check with Lemay/Labaree. |
| 13 | Margaret Barton Korty, *Benjamin Franklin and Eighteenth-Century American Libraries*, 1965. <https://doi.org/10.2307/1005702> | Academic article/monograph; high. | Focused source for Library Company as a Junto-derived knowledge asset. |
| 14 | Edwin Wolf 2nd, *At the Instance of Benjamin Franklin: A Brief History of the Library Company of Philadelphia*, 1976/1995. <https://librarycompany.org/> | Institutional history; high. | Use for subscription library mechanics and access caveats. |
| 15 | Benjamin Franklin, *A Modest Enquiry into the Nature and Necessity of a Paper-Currency*, 1729. <https://founders.archives.gov/documents/Franklin/01-01-02-0041> | Primary pamphlet in scholarly edition; high. | Example of discussion-to-public-argument workflow. |
| 16 | American Philosophical Society history / Franklin founding context. <https://www.amphilsoc.org/> | Institutional archive/learned society source; high. | APS is downstream/adjacent to Junto tradition, not simply the Junto renamed. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `franklin-query-convener` | `person` | high | Self-reported organizer; use as query designer, not omniscient founder-avatar. |
| `breintnall-reader-naturalist` | `person` | medium-high | Mostly visible through Franklin; use for poetry, reading, and curiosity. |
| `godfrey-mathematical-critic` | `person` | medium-high | Franklin's sketch may be unfair; use for precision and instrument-minded critique. |
| `scull-parsons-surveyor-seat` | `role` | high for role | Combine only for measurement, mapping, land, astronomy, and practical geography. |
| `coleman-cool-judgment` | `person` | medium-high | Heavily filtered through Franklin's praise. |
| `grace-patron-prototyper` | `person` | medium | Thin independent source base; use for patronage, wit, and material prototyping. |
| `junto-moderator` | `role` | high | Not a named persona; enforces discipline, turn-taking, and anti-victory norms. |
| `deserving-stranger` | `exemplar` | high | Derived from Junto questions; models outward-facing aid and onboarding. |

## Parishad

Configuration direction: source-constrained interpretive council for legal,
ethical, role, and stakeholder tradeoffs. Use roles and textual exemplars rather
than stable named historical members.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Patrick Olivelle, *Manu's Code of Law: A Critical Edition and Translation of the Manava-Dharmasastra*, Oxford University Press, 2005. ISBN `9780195171464`. | Primary dharma text in critical scholarly translation; high. | Main anchor for parishad composition and source hierarchy. Normative Brahmanical jurisprudence, not enacted positive law. |
| 2 | Georg Buhler, *The Laws of Manu*, 1886, Sacred Books of the East 25. Manu XII online: <https://www.sacred-texts.com/hin/manu/manu12.htm> | Older public-domain primary translation; medium-high, outdated. | Public anchor for Manu 12.105-115, including ten-person or three-person legal assembly. |
| 3 | Patrick Olivelle, *Dharmasutras: The Law Codes of Ancient India*, Oxford University Press, 1999. ISBN `9780192838827`. | Primary dharmasutra translations; high. | Early sources of dharma, tradition, learned custom, and contextual uncertainty. |
| 4 | Georg Buhler, *The Sacred Laws of the Aryas*, SBE 2 and 14, 1879/1882. <https://www.sacred-texts.com/hin/sbe02/index.htm> | Older primary translations; medium. | Public backup for Apastamba, Gautama, Baudhayana, and Vasistha; check terminology against modern work. |
| 5 | Richard W. Lariviere, *The Naradasmrti*, 1989; rev. 2003. | Primary legal/procedure text in critical translation; high. | Best source for court procedure, pleading, evidence, and titles of law. |
| 6 | *Naradasmrti* Sanskrit / older translations. SARIT: <https://sarit.indology.info/sarit-pm/works/naradasmrti.xml?view=div>; Jolly scan: <https://archive.org/details/naradiyadharmasa021669mbp/page/n1/mode/2up> | Primary text access; SARIT high, Jolly older. | Useful for quote-checking terms; not final interpretive authority. |
| 7 | Julius Jolly, *The Minor Law-Books*, SBE 33, 1889. | Older primary translations; medium. | Narada and Brihaspati support procedural and judicial lenses. |
| 8 | Patrick Olivelle, *King, Governance, and Law in Ancient India: Kautilya's Arthasastra*, Oxford University Press, 2013. ISBN `9780199891825`. | Primary statecraft/legal text in modern translation; high. | Adds administrative/enforcement counterweight. Do not merge source families without labeling. |
| 9 | P. V. Kane, *History of Dharmasastra*, 1930-1962. Archive search: <https://archive.org/search.php?query=creator%3A%22P.+V.+Kane%22> | Monumental secondary reference; high but older. | Use for variant terms, chronology, and cross-text references. |
| 10 | Robert Lingat, *The Classical Law of India*, trans. J. D. M. Derrett, 1973. | Classic academic synthesis; high. | Models law as plural, interpretive, and embedded in custom, kingly authority, and Brahmanical expertise. |
| 11 | Donald R. Davis Jr., *The Spirit of Hindu Law*, Cambridge University Press, 2010. | Modern academic synthesis; high. | Corrects against treating Manu as simple statutory code. |
| 12 | Timothy Lubin, Donald R. Davis Jr., and Jayanth K. Krishnan, eds., *Hinduism and Law: An Introduction*, Cambridge University Press, 2010. | Academic edited volume; high. | Good background for Indic authority, tradition, colonial reception, and practice. |
| 13 | Donald R. Davis Jr., "Hinduism as a Legal Tradition," *Journal of the American Academy of Religion* 75.2 (2007), 241-267. <https://doi.org/10.1093/jaarel/lfm004> | Peer-reviewed article; high. | Concise framing for legal tradition without modern statutory assumptions. |
| 14 | J. D. M. Derrett, "The Administration of Hindu Law by the British," *Comparative Studies in Society and History* 4.1 (1961), 10-52. <https://doi.org/10.1017/S0010417500001213> | Peer-reviewed article; high. | Corrects colonial distortions and court/pandit mediation issues. |
| 15 | Ludo Rocher, "Law Books in an Oral Culture: The Indian Dharmasastras," *Proceedings of the American Philosophical Society* 137 (1993), 254-267. | Learned-society article; high. | Important caution against treating textual law books as straightforward enacted law. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `dharmadhikarin-chair` | `role` | medium | Useful chair label, but not the core Manu 12.111 role list. |
| `veda-specialist-triad` | `role` | high | Textual authority lens; not broad social representation. |
| `mimamsaka-hermeneutician` | `role` | high | Interprets injunctions and conflicts; not generic ethics. |
| `tarkika-logician` | `role` | high | Reasoning must remain source-constrained. |
| `nirukta-philologist` | `role` | high | Handles meaning, etymology, and technical terms. |
| `dharmasastra-reciter` | `role` | high | Source-reciter/exegete, not modern lawyer. |
| `brahmacarin-student` | `role` | medium | Life-stage duty lens; avoid modern youth-advocate framing. |
| `grhastha-householder` | `role` | medium-high | Household/property/kinship lens; historically male and elite-biased. |
| `ascetic-life-stage` | `role` | medium | Manu's life-stage wording is ambiguous; keep caveated. |
| `sista-custom-representative` | `role` | medium | Learned custom, not democratic local opinion. |
| `narada-procedure-exemplar` | `exemplar` | medium | Attributed textual sage, not stable historical person. |

## Seven Sages

Configuration direction: bounded synthesis from up to seven practical-wisdom
lenses. Use a Plato-style default roster, while preserving list variance and
late attribution uncertainty.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Plato, *Protagoras* 342e-343b. Project Gutenberg Jowett translation: <https://www.gutenberg.org/ebooks/1591> | Primary dialogue; earliest explicit canonical-style list. | Default roster anchor: Thales, Pittacus, Bias, Solon, Cleobulus, Myson, Chilon. |
| 2 | Diogenes Laertius, *Lives of Eminent Philosophers*, Book 1, Loeb trans. R. D. Hicks, 1925. <https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diogenes_Laertius/home.html> | Ancient doxography; late but indispensable. | Directly supports list variance, anecdotes, sayings, and larger candidate pools. |
| 3 | Plutarch, *The Dinner of the Seven Wise Men*, Loeb trans. F. C. Babbitt, 1928. <https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Moralia/Dinner_of_the_Seven%2A.html> | Primary literary symposium; not historical transcript. | Useful for convening mechanics, practical questions, wit, and Anacharsis variant. |
| 4 | Pausanias, *Description of Greece* 10.24.1. Perseus/Loeb locator: `Paus. 10.24.1`. | Primary travel description; credible for site tradition. | Supports Delphic inscription context, not secure individual authorship. |
| 5 | Stobaeus, *Anthology* / *Florilegium*, "Sayings of the Seven Sages," locator `Stob. Anth. 3.1`. | Late primary anthology; useful but attribution-uncertain. | Source for aphoristic counsel mode and larger maxim corpus. |
| 6 | Herodotus, *Histories* 4.76-78, Loeb trans. 1921. <https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Herodotus/4C%2A.html> | Primary history; early. | Supports Anacharsis as notable outsider figure, not canonical membership. |
| 7 | Aristotle, *Politics* 1.11, 1259a. <https://classics.mit.edu/Aristotle/politics.1.one.html> | Primary philosophical/political text. | Thales olive-press anecdote supports practical leverage from knowledge. |
| 8 | Diodorus Siculus, *Bibliotheca historica* fragments on sages/maxims. Loeb/Perseus locator. | Primary historical compilation; late. | Corroborating tradition for maxim ambiguity and sage anecdotes. |
| 9 | Ausonius, *Ludus Septem Sapientum* / *The Masque of the Seven Sages*. | Late antique primary literary text. | Shows later canonical dramatization and Periander substitution. |
| 10 | Jona Lendering, "Seven Sages," Livius, 2004; updated 2020. <https://www.livius.org/articles/people/seven-sages/> | Specialist reference; concise and transparent. | Best compact source for list variance: four highly stable names and many candidates for remaining slots. |
| 11 | Bruno Snell, ed., *Leben und Meinungen der Sieben Weisen*, Munich: Heimeran, 1971. | Scholarly source collection; high. | Deep source for Greek/Latin testimonia and variants. |
| 12 | H. W. Parke and D. E. W. Wormell, *The Delphic Oracle*, vol. 1, Basil Blackwell, 1956, pp. 387-389. | Academic monograph; standard. | Constrains claims about Delphic maxim authorship. |
| 13 | G. S. Kirk, J. E. Raven, and M. Schofield, *The Presocratic Philosophers*, 2nd ed., Cambridge University Press, 1983. | Academic textbook/sourcebook; high. | Treats Thales differently from most sages: stronger philosophical/scientific reception. |
| 14 | Leslie Kurke, *Aesopic Conversations: Popular Tradition, Cultural Dialogue, and the Invention of Greek Prose*, Princeton University Press, 2011. ISBN `9780691144580`. | Academic monograph; high. | Supports Aesop as optional popular/fable-wisdom exemplar, not strict default sage. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `thales-practical-leverage` | `person` | high | Strong reception, but direct writings are absent or doubtful. |
| `solon-lawgiver` | `person` | high | Better historical footprint than most, but later traditions reshape him. |
| `pittacus-civic-moderator` | `person` | medium-high | Stable in lists; sayings and governing role are source-mediated. |
| `bias-legal-diplomat` | `person` | medium-high | Stable in lists; mostly anecdotal legal/diplomatic wisdom. |
| `chilon-laconic-discipline` | `person` | medium | Later Spartan idealization is a risk. |
| `cleobulus-riddle-moderation` | `person` | medium | Evidence is thinner and entangled with tyranny/riddle traditions. |
| `myson-obscure-default` | `person` | medium | Plato-backed default; otherwise obscure and often replaced. |
| `anacharsis-outsider-critic` | `exemplar` | medium | Greek sources may project Greek concerns onto a Scythian figure. |
| `periander-power-warning` | `exemplar` | medium | Contested tyrant figure; must carry power-abuse warning. |
| `aesop-popular-counterwisdom` | `exemplar` | medium | Not canonical in the strict default list. |

## Yushitai

Configuration direction: accountability, remonstrance, inspection paths, and
failure-mode detection. Use office roles across imperial censorial traditions;
do not pretend a single stable office design held across all dynasties.

### Sources

| # | Resource | Type / credibility | Implementation notes |
| --- | --- | --- | --- |
| 1 | Charles O. Hucker, *The Censorial System of Ming China*, Stanford University Press, 1966. | Academic monograph; highest-priority specialist source for Ming censorial institutions. | Best anchor for role design: surveillance, impeachment, remonstrance, tours, and institutional constraints. |
| 2 | Charles O. Hucker, *A Dictionary of Official Titles in Imperial China*, Stanford University Press, 1985. Harvard OCR locator: <http://projects.iq.harvard.edu/files/cbdb/files/hucker_official_titles_ocr_searchable_all_pages.pdf> | Specialist reference; high. | Use for official-title mappings and avoiding false equivalence across dynasties. |
| 3 | Charles O. Hucker, "Governmental Organization of The Ming Dynasty," *Harvard Journal of Asiatic Studies* 21 (1958), 1-66. | Peer-reviewed article; high. | Concise institutional map for Ming government and Censorate placement. |
| 4 | Yü-Ch'üan Wang, "An Outline of the Central Government of the Former Han Dynasty," *Harvard Journal of Asiatic Studies* 12.1/2 (1949), 134-187. | Peer-reviewed article; high. | Supports early imperial censorial powers and Imperial Counselor lineage. |
| 5 | Michael Loewe, *The Government of the Qin and Han Empires, 221 BCE-220 CE*, Hackett, 2006. | Academic monograph; high. | Use for early imperial administrative context and censorial evolution. |
| 6 | Hans Bielenstein, *The Bureaucracy of Han Times*, Cambridge University Press, 1980. | Academic monograph; high. | Strong source for Han offices, ranks, and supervisory roles. |
| 7 | Denis Twitchett and Michael Loewe, eds., *The Cambridge History of China, Vol. 1: The Ch'in and Han Empires, 221 B.C.-A.D. 220*, Cambridge University Press, 1986. | Academic synthesis; high. | Background for Qin-Han central government and early censorial office development. |
| 8 | Frederick W. Mote and Denis Twitchett, eds., *The Cambridge History of China, Vol. 8: The Ming Dynasty, Part 2, 1368-1644*, Cambridge University Press, 1998. | Academic synthesis; high. | Includes Ming government context; supports Hucker's institutional claims. |
| 9 | Ray Huang, *1587, A Year of No Significance: The Ming Dynasty in Decline*, Yale University Press, 1981. | Academic narrative; high. | Useful for lived politics of remonstrance, moral criticism, and bureaucratic friction. |
| 10 | John W. Dardess, *Confucianism and Autocracy: Professional Elites in the Founding of the Ming Dynasty*, University of California Press, 1983. | Academic monograph; high. | Supports tension between professional elites, imperial authority, and surveillance. |
| 11 | R. Kent Guy, *Qing Governors and Their Provinces: The Evolution of Territorial Administration in China, 1644-1796*, University of Washington Press, 2010. | Academic monograph; high. | Useful for local/provincial monitoring context and limits of central inspection. |
| 12 | Beatrice S. Bartlett, *Monarchs and Ministers: The Grand Council in Mid-Ch'ing China, 1723-1820*, University of California Press, 1991. | Academic monograph; high. | Broader Qing central governance context; useful for not over-isolating the Censorate. |
| 13 | *Ming shi* (History of Ming), Treatise on Officials. | Primary dynastic history; high but compiled after the dynasty. | Use for official-title lineage and formal institutional description; cross-check with Hucker. |
| 14 | *Da Ming huidian* (Collected Statutes of the Great Ming). | Primary administrative code; high for formal rules. | Use for formal office definitions and procedures; not sufficient for actual practice. |

### Representative Lens Direction

| Lens | Type | Confidence | Limitation |
| --- | --- | --- | --- |
| `censor-in-chief` | `role` | high | Office functions shift by dynasty; source notes must name the period. |
| `investigating-censor` | `role` | high | Strong inspection/impeachment lens; not a general reviewer. |
| `remonstrance-censor` | `role` | medium-high | Useful for speaking upward, but historical remonstrance could be politicized. |
| `palace-audience-censor` | `role` | medium | Period-specific; use for access/control of court-facing critique. |
| `circuit-inspection-censor` | `role` | high | Good lens for field evidence, local failure, and anti-capture checks. |
| `discipline-impeachment-censor` | `role` | high | Focuses on misconduct classification and documented accusation. |
| `control-yuan-successor` | `exemplar` | low-medium | Modern successor analogy only; do not project it backward into imperial Yushitai. |

## Cross-Method Claims To Avoid

- Do not make historical representatives always-on. They are explicit-only
  source lenses.
- Do not invent stable named rosters for Areopagus, Parishad, or Yushitai.
- Do not collapse Areopagus and Yushitai into the same "red team" wrapper:
  Areopagus is constrained adjudicative review; Yushitai is inspection and
  accountability.
- Do not make Seven Sages a fixed universal roster. Record default and variants.
- Do not reduce Junto to debate. It is query preparation, mutual aid, disciplined
  conversation, and civic artifact production.
- Do not treat Jixia as a single doctrine. It is pluralist, patronage-backed,
  and source-fragmentary.
