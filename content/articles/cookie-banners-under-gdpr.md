---
title: What a cookie banner must actually do under GDPR
topic: Consent
weight: 1
summary: The cookie banner is the most visible part of privacy compliance and one of the most often built wrongly. The legal test is short. The implementation is where it breaks.
blurb: The legal test is short. The implementation is where it usually breaks: what loads before a choice, how refusal compares with acceptance, and how withdrawal works.
---
## Two laws, one banner

In the EU, two instruments apply. Article 5(3) of the ePrivacy Directive requires consent before information is stored on, or read from, a user's device, unless the storage is strictly necessary to provide a service the user asked for. The GDPR then supplies the definition of consent that the ePrivacy rule borrows.

## What counts as consent

Article 4(11) GDPR defines consent as a freely given, specific, informed and unambiguous indication of the person's wishes, given by a statement or a clear affirmative action. Each word does work in a banner.

Unambiguous and affirmative rules out pre-ticked boxes. The Court of Justice of the EU held exactly that in Planet49 (Case C-673/17). Specific means a visitor can say yes to analytics and no to advertising, rather than accepting a bundle. Informed means the purposes and the parties involved are visible before the choice, not after it.

Freely given has the most practical consequence. European regulators, including the French CNIL, have penalised sites where refusing took more steps than accepting. Article 7(3) adds that withdrawing consent must be as easy as giving it, so a banner that disappears and cannot be reopened is a problem of its own.

## Where implementations fail

The most common failure is invisible to the person looking at the banner: tags that fire before any choice is made. A banner can look compliant while analytics and advertising scripts have already loaded, which makes the consent decorative. The check that matters is a network inspection of the page before interaction, not a review of the banner's wording.

The second is drift. Cookie lists go stale as sites add vendors, so a banner describes cookies that no longer exist and omits ones that do. Regular scanning is part of the obligation to be informative, not an optional extra.

## Beyond the EU

One banner design does not travel unchanged. California works on notice and opt-out rather than prior consent, and its rules expect opt-out preference signals such as Global Privacy Control to be honoured. Brazil's LGPD and South Africa's POPIA rest on a set of legal bases, of which consent is only one. A product that serves all of these needs behaviour that varies by region, not a single global default.
