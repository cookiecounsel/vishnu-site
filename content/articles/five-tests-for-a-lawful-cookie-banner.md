---
title: Five tests for a lawful cookie banner
date: 2026-11-13
topic: Consent
summary: "A cookie banner is lawful when five things are true. Most failures
  come from the same few mistakes: loading trackers early, hiding the reject
  option, and keeping no proof of the visitor's choice."
draft: false
---
---

A cookie banner looks like a design problem, but it is a legal instrument. Its job is to produce valid consent before anything non-essential runs on the visitor's device, and to leave a record that proves it did. These are the five tests I apply when I review one. They are drawn from EU law, because that is where the case law and regulatory practice are, with a short note at the end on how India's new regime compares.

## 1. Nothing non-essential loads before the visitor chooses

The ePrivacy rules on storing and reading information on a person's device require consent first, subject to a narrow exemption for what is strictly necessary. That is a rule about timing, not about the wording of the banner. Wording matters too, but it is governed by the GDPR's standard for valid consent, which the ePrivacy rules borrow, and not by the ePrivacy rule itself. A banner that appears while analytics and advertising scripts are already firing in the background has not obtained consent. It has announced a decision that was already made on the visitor's behalf, and that is not compliant.

The practical check is simple. Open the site in a clean browser, leave the banner untouched, and look at the cookies and network requests. Anything beyond what the page strictly requires to function is a failure of this test, however good the banner looks.

## 2. In the EU, consent is an active choice, never a default

The GDPR's recitals say that silence, pre-ticked boxes or inactivity cannot amount to consent. The Court of Justice applied that to cookies in Planet49 in October 2019, holding that a pre-ticked checkbox which the visitor must untick to refuse does not produce valid consent. The reason lies in the definition of consent in Article 4(11), which requires an unambiguous indication of the visitor's wishes by a statement or a clear affirmative action. A pre-ticked box means the website has taken the decision for the visitor, so there is no choice of the visitor's own to point to, and no way of telling objectively whether they agreed. Scrolling, continuing to browse, or closing a banner is not a choice either. The same holds for the second layer of a banner: toggles for optional categories must start in the off position.

The position in the United States is largely the reverse. Most state privacy laws let tracking run by default and give the visitor a right to opt out, with exceptions such as sensitive data, where opt-in consent is generally required. So this test describes the European standard, not a universal one.

## 3. Refusing is as easy as accepting

This is where most banners fail in practice. In January 2022 the French regulator, the CNIL, fined Google 150 million euros and Facebook 60 million euros because accepting took one click while refusing took several. Its reasoning was that a harder refusal path steers the visitor towards accepting, which undermines the freedom of the consent.

In January 2023 the European Data Protection Board published the report of its cookie banner taskforce. The report is not formal EDPB guidance, and it records some disagreement among authorities. But the position of the large majority was clear: a banner with an accept button on its first layer should also offer a reject option there, and deceptive design, such as a faint link in place of a button, undermines consent. The safe design is accept, reject and manage choices, equally visible, in the same place, with similar prominence.

## 4. Withdrawal is as easy as giving consent

Article 7(3) of the GDPR gives the visitor the right to withdraw consent at any time and says it must be as easy to withdraw as to give. For a banner this means a permanent, findable control, usually a small link in the footer, that reopens the choices on any page. If a visitor accepted with one click, forcing them to email the site to undo it fails the test. Withdrawal must also actually work: once consent is withdrawn, the scripts that depended on it must stop.

## 5. You can prove what was chosen

Article 7(1) puts the burden on the controller to demonstrate that the data subject consented. A banner that works but keeps no record leaves the business unable to prove anything if a regulator or a complainant asks. A usable consent record shows what the visitor was shown, what they chose, and when, and it is tied to the version of the banner and the cookie list in force at that moment. The CNIL has said that sites should keep a record of refusals for at least six months, which is a useful working benchmark even outside France.

## A note on essential cookies

All five tests depend on the line between essential and non-essential cookies being drawn honestly. The taskforce specifically identified wrongly labelling cookies as strictly necessary, so that no consent is requested for them, as a common infringement. A cookie is exempt because the service the visitor asked for cannot work without it, not because the business finds it useful.

## A note for the legitimate interest enthusiasts

Legitimate interest is a lawful basis under Article 6(1)(f) of the GDPR, and it is tempting to reach for it when consent looks commercially inconvenient. For placing or reading a non-essential cookie, it is not available. Article 5(3) of the ePrivacy Directive requires consent for that step, and the European Data Protection Board's Opinion 5/2019 treats Article 5(3) as the more specific rule, which prevails: the controller cannot choose from the full list of Article 6 grounds for the act of storing or reading the cookie. The exemption for strictly necessary cookies is a separate, narrow carve-out and is not a legitimate interest test. Measuring your audience may well be in your interest, but it does not make analytics essential.

Legitimate interest can, in principle, still have a role later, for the subsequent processing of data that was lawfully collected through a cookie, provided the controller has a valid Article 6 basis for that stage. It cannot repair a consent that was never obtained. The cookie banner taskforce found a recurring pattern in which a first layer asks for consent and a second layer lists the same purposes as "legitimate interests" with an objection toggle. Its view was that this confuses visitors into thinking they must refuse twice, and that a banner relying on legitimate interest for non-essential cookies is not collecting valid consent. In practice, "reject all" must cover every non-essential purpose, with no separate legitimate interest switches for tracking.

The same logic applies after a refusal or a withdrawal. A controller cannot quietly move the same processing onto legitimate interest in order to carry on.

## How India compares

India's Digital Personal Data Protection Act asks for consent that is free, specific, informed, unconditional and unambiguous, given by a clear affirmative action, and it says withdrawal must be as easy as giving consent. It also requires a notice to accompany or precede the request. The substantive obligations under the Rules are due to apply from 13 May 2027. In substance these tests carry across, and a banner built to pass them is a sound starting point for Indian users too, though the Indian regime has its own notice requirements and its own consent manager framework, which deserve a separate discussion.

## Sources

- [Report of the EDPB Cookie Banner Taskforce, adopted 17 January 2023](https://www.edpb.europa.eu/system/files/2023-01/edpb_20230118_report_cookie_banner_taskforce_en.pdf)
- [CNIL fines against Google and Facebook, January 2022, as reported by SCL](https://www.scl.org/12482-french-data-protection-regulator-fines-google-and-facebook-for-making-it-harder-to-refuse-cookies-than-to-accept-them/)
- [EDPB Opinion 5/2019 on the interplay between the ePrivacy Directive and the GDPR](https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-52019-interplay-between-eprivacy_en)
- [Judgment of the Court of Justice in Planet49, Case C-673/17, 1 October 2019](http://curia.europa.eu/juris/document/document.jsf?text=&docid=218462&pageIndex=0&doclang=EN&mode=lst&dir=&occ=first&part=1&cid=1490926)
- GDPR, Articles 7(1) and 7(3) and Recital 32
- Digital Personal Data Protection Act, 2023, sections 5 and 6, and the Digital Personal Data Protection Rules, 2025

