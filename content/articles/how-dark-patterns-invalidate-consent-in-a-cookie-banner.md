---
title: How dark patterns invalidate consent in a cookie banner
date: 2026-11-16
topic: Consent
summary: "A banner can load nothing early, record every choice and still produce invalid consent, because its design steers the visitor. Where dark patterns break the definition of consent in Article 4(11) GDPR, and what follows."
description: "How dark patterns in cookie banners conflict with the GDPR definition of consent: freely given, specific, informed and unambiguous, and the consequences."
updated: 2026-11-16
draft: false
---

Cookie banners are usually reviewed for their mechanics: whether cookies fire before consent, how choices are recorded, and so on. These checks matter, but they are not enough. The other half of the question is how the interface of the banner interacts with the visitor. This is where dark patterns arise, and it is the most underestimated part of having a compliant banner.

## Design as a legal question

The GDPR does not use the term "dark patterns". The requirement for a banner free of them comes from what the GDPR already requires: the conditions for valid consent under Article 4(11) and Article 7, the principle of fair and transparent processing in Article 5(1)(a), and the duty to build data protection into the design of a system under Article 25.

The most useful interpretive source is the EDPB's Guidelines 03/2022, published in final form in February 2023. They define the practice as interface design that leads people to make unintended or harmful decisions about their data, and they sort it into six categories: overloading, skipping, stirring, hindering, fickle and left in the dark. (You can see what these are towards the end of this article.) The Guidelines should be read with two cautions. First, they were written for social media platform interfaces, so their application to a cookie banner is by analogy and not direct, although their reasoning carries over. Second, they are guidance, not law. Their weight comes from the fact that supervisory authorities use them when deciding cases.

The next source is more specific to banners. In January 2023, the EDPB's Cookie Banner Taskforce published a report on how authorities were handling the complaints they had received about banner design. It interprets the ePrivacy rules on cookies, which borrow the definition of consent from the GDPR, and not the GDPR itself. This article relies on both documents.

## How a banner fails the definition of consent

It is easy to stop at the basics. Anyone looking up how to set up a consent banner will learn that a banner must be shown and that cookies and other data-collecting technologies must not fire before consent. Many operators stop there and assume that this is all that is required.

It is not. Dark patterns are caught mainly through the definition of consent in Article 4(11), which requires consent to be freely given, specific, informed and unambiguous. A dark pattern conflicts with this definition, and in different ways. It helps to take the elements one at a time.

**Freely given.** The most recognisable pattern is the asymmetry between accepting and refusing: a prominent "Accept all" button next to a reject option that is smaller, paler, rendered as a link, or placed on a second layer. The Taskforce records that a vast majority of authorities consider a banner without a reject option alongside the accept option inconsistent with valid consent, and it treated the use of a link rather than a button for refusal as potentially deceptive. The point is that a choice offered on unequal terms, in this case one that nudges the visitor to accept because accepting is easier than rejecting, is not a free one.

**Unambiguous.** Consent requires a clear affirmative act. A pre-ticked box fails that test, as the Court of Justice held in Planet49. So does any design that treats scrolling, continued browsing or closing the banner as agreement.

**Informed.** People can be led to choose an option they did not intend simply by the way information is presented, and a consent banner is no exception. Wording can steer as effectively as colour. Emotive phrasing, labels that obscure what a button does, and purposes described in terms too vague to understand all work against an informed choice. The Taskforce also noted that button colour and contrast can mislead a visitor into giving consent they did not intend, which puts the problem in the visitor's understanding of the act and not only in their freedom to refuse.

**Specific.** Consent must be given for a particular purpose. A visitor may be willing to accept the cookies that make an embedded video play, but not the marketing cookies. They should be able to accept the first and refuse the others. A single "Accept all" button that covers analytics, advertising and other third-party cookies, with no option to decline one category while accepting another, does not produce valid consent. The same is true of a second layer whose "Save" button does not let the visitor choose the categories they agree to.

The same banner often fails on more than one of these at once, and a regulator will not care which label an operator would prefer. In short, a banner that passes the technical checks can still fail the definition of consent.

## Where emphasis becomes obstruction

Operators sometimes argue that giving the main action a stronger colour is ordinary interface design, and that a banner is not invalid merely because one button stands out. That argument assumes that accepting is the main action, and nobody gets to decide that. Under the consent rules the visitor's yes and no carry equal weight, so a banner that ranks one above the other has already leaned on the answer. Even so, the Taskforce accepted that each banner has to be assessed on its facts, and a [law-firm summary of the report](https://www.lewissilkin.com/en/insights/2025/02/04/cnil-cracks-down-on-dark-patterns-in-cookie-banners-102jv0a) is more cautious than its headline suggests.

The practical line is cumulative. One visual difference may be defensible. Different colour, smaller size, lower contrast, weaker wording and an extra click, taken together, describe a banner built to produce acceptance. The EDPB's own preference shows the standard it has in mind: the buttons should ideally share the same size, colour, font and contrast, so that no option is made easier to choose than another. If you are assessing a design, ask what a visitor would do if they paid no attention, and whether the banner has been arranged so that the answer is "accept".

## Refusal that does not refuse

The patterns above concern what the visitor sees. A more serious failure concerns what happens afterwards. A reject button that leaves non-essential trackers running is the clearest case of an interface that offers a choice and does not honour it. The CNIL's decision against SHEIN in September 2025, which carried a fine of €150 million, concerned inadequate mechanisms for refusing and withdrawing consent, among other findings. I would read the decision itself before relying on its details, since summaries of it differ in emphasis.

## Consequences of invalid consent

An invalid consent means that there are consequences that follow the act. First, the processing loses its legal basis. The GDPR does not allow personal data to be processed freely: under Article 6, every processing activity needs one of six legal bases, and consent under Article 6(1)(a) is one of them. When a banner collects consent and the data is processed on the strength of it, that consent is the basis. If the consent turns out to be invalid, the basis falls away, and so does the lawfulness of everything that depended on it: the cookies set, the data collected through them and the uses made of that data downstream. There is also no easy way out. Where the ePrivacy rules require consent for a cookie, a site cannot replace it with another basis, such as legitimate interests, once the consent has failed.

Second, the failure itself carries a penalty. The GDPR has two tiers of administrative fines. The lower tier goes up to €10 million or 2% of worldwide annual turnover, and the higher tier goes up to €20 million or 4%, whichever is higher in each case. Article 83(5)(a) puts the conditions for consent in the higher tier, alongside the basic principles of processing. These figures are ceilings and not fixed amounts: the authority sets the actual fine after looking at the circumstances, such as how serious the infringement was, how long it lasted and how many people were affected.

Third, cookie rules are often enforced under a different law from the GDPR. Cookies sit under two layers of law: the GDPR, which governs what happens to the personal data, and the ePrivacy Directive, which governs storing or reading information on a visitor's device in the first place. The ePrivacy Directive is applied through national laws. In France that law is the French Data Protection Act, and its Article 82 is what the CNIL cited in its December 2024 notices to publishers, which gave them one month to change banners that nudged visitors to accept. This route matters because the GDPR's one-stop-shop mechanism, under which a company active in several EU countries normally answers to one lead authority, does not apply to these rules. A national authority can therefore act directly against a site serving its residents.

On 27 November 2025 the CNIL fined American Express Carte France €1.5 million under Article 82 of the French Data Protection Act. It found that advertising cookies were placed as soon as a visitor arrived, before any choice was made, that they were still placed after the visitor refused, and that cookies already placed continued to be read after consent was withdrawn.

## Who answers for the design

The site operator is the controller of the consent it collects, and Article 24 and Article 25 put the responsibility for appropriate design on the controller. In practice most banners are built from a template supplied by a consent management tool, with colours, labels and defaults left for the operator to configure. The responsibility does not move with the template. An operator who switches on a vendor's default layout without checking it has still chosen the design.

The practical conclusion is also a legal one. In the usual arrangement the consent management tool is a processor, acting on the website owner's instructions, while the website owner is the controller who decides how consent is collected and answers for it. A processor cannot take that responsibility over. The person responsible for the site should therefore look at what the banner actually displays, in each language and on each device, and not at what the tool's description says it displays.

## Reviewing your own banner

Five questions cover most of the ground. How many actions does it take to accept, and how many to refuse? Do the accept and reject options share size, colour, font and contrast? Does the wording describe what each choice does, in neutral terms? On the second layer, is anything switched on by default, and does "Save" mean what it says? And after refusing, with the browser's network tool open, does anything non-essential still load?

A banner that answers all five well has dealt with the main design risks. One that answers any of them badly has given a regulator a reason to look at the rest.

## The EDPB's six categories

The Guidelines were written for social media interfaces, but the six categories describe behaviour that also appears in cookie banners. The banner examples below are illustrations of how each category might look, not examples taken from the Guidelines.

**Overloading** burdens the person with so many requests, notices or options that they give in. The sub-types include continuous prompting, a privacy maze and too many options. In a banner this could be a long list of vendors, each with its own toggle, and no simple way to refuse them all.

**Skipping** designs the interface so that people overlook or forget the data protection aspects of a decision. The sub-types are deceptive snugness, where the most intrusive settings are on by default, and look over there, where attention is drawn away from the privacy choice. A pre-enabled marketing toggle is the banner version.

**Stirring** appeals to emotion or uses visual nudges to steer the choice. Wording that makes refusal sound reckless, or a bright accept button beside a grey reject link, belongs here.

**Hindering** obstructs or blocks people from getting information or managing their data, by making an action difficult or impossible. The sub-types include longer than necessary and misleading action. A reject option that takes several clicks, or a withdrawal control that is hard to find, are examples.

**Fickle** means an inconsistent or unclear interface, in which it is hard to find the controls or to understand what they do. Lacking hierarchy and decontextualising are among its sub-types. A banner whose labels or button positions change between layers is an example.

**Left in the dark** hides information or controls, or leaves people unsure how their data is handled and what control they have over it. A banner whose wording contradicts the cookie policy it links to, or which appears in a language different from the rest of the site, would fit.

## Sources

- Regulation (EU) 2016/679 (GDPR), Articles 4(11), 5, 6, 7, 24, 25 and 83: [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- EDPB, Guidelines 03/2022 on deceptive design patterns in social media platform interfaces, final version February 2023
- EDPB, [Report of the work undertaken by the Cookie Banner Taskforce](https://edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf), adopted 17 January 2023
- Court of Justice of the EU, Planet49, Case C-673/17
- CNIL, [Cookies placed without consent: SHEIN fined 150 million euros](https://www.cnil.fr/en/cookies-placed-without-consent-shein-fined-150-million-euros-cnil), September 2025
- CNIL, [Cookies: AMERICAN EXPRESS fined €1.5 million by the CNIL](https://cnil.fr/en/node/167842), December 2025
- Lewis Silkin, [CNIL cracks down on dark patterns in cookie banners](https://www.lewissilkin.com/en/insights/2025/02/04/cnil-cracks-down-on-dark-patterns-in-cookie-banners-102jv0a), February 2025
