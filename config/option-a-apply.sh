#!/bin/sh
# Apply the Option A categories and tags to spbw.beer with WP-CLI.
# Run from the WordPress folder as the site user. BACK UP THE SITE FIRST.
# Dry run by default (prints the commands). Run with DRY_RUN=0 to apply them.
if [ "${DRY_RUN:-1}" = "0" ]; then RUN=""; else RUN="echo"; fi

# 1. Existing categories are reused by name; new ones are created as needed.

$RUN wp post term add 408 category 'Society News'
$RUN wp post term add 414 category 'Society News'
$RUN wp post term add 416 category 'Society News'
$RUN wp post term add 416 post_tag 'Beer from the Wood'
$RUN wp post term add 467 category 'Society News'
$RUN wp post term add 1180 category Event
$RUN wp post term add 1180 post_tag 'Beer from the Wood'
$RUN wp post term add 1557 category Event
$RUN wp post term add 1557 category Woodfest
$RUN wp post term add 1557 post_tag Woodfest
$RUN wp post term add 1625 category Event
$RUN wp post term add 1625 post_tag 'Beer from the Wood'
$RUN wp post term add 1634 category Event
$RUN wp post term add 1634 post_tag Anniversary
$RUN wp post term add 1795 category Event
$RUN wp post term add 1795 post_tag 'Bill English'
$RUN wp post term add 1885 category Shop
$RUN wp post term add 1916 category Event
$RUN wp post term add 1916 post_tag AGM
$RUN wp post term add 1940 category Event
$RUN wp post term add 1940 post_tag AGM
$RUN wp post term add 1996 category Event
$RUN wp post term add 1996 post_tag 'Beer from the Wood'
$RUN wp post term add 2032 category 'Branch News'
$RUN wp post term add 2032 post_tag 'Greater Manchester'
$RUN wp post term add 2046 category 'Branch News'
$RUN wp post term add 2069 category Event
$RUN wp post term add 2069 post_tag Quiz
$RUN wp post term add 2092 category 'Branch News'
$RUN wp post term add 2104 category Event
$RUN wp post term add 2104 post_tag Anniversary
$RUN wp post term add 2111 category Event
$RUN wp post term add 2111 post_tag 'Beer Festival'
$RUN wp post term add 2141 category Shop
$RUN wp post term add 2141 post_tag 'Polo Shirts'
$RUN wp post term add 2146 category 'Branch News'
$RUN wp post term add 2146 post_tag COBRA-COW
$RUN wp post term add 2170 category Event
$RUN wp post term add 2170 post_tag 'Beer and Curry'
$RUN wp post term add 2177 category Event
$RUN wp post term add 2177 category 'Branch News'
$RUN wp post term add 2177 post_tag Memorial
$RUN wp post term add 2177 post_tag Walk
$RUN wp post term add 3588 category Shop
$RUN wp post term add 3659 category Event
$RUN wp post term add 3659 category 'Branch News'
$RUN wp post term add 3659 post_tag 'Greater Manchester'
$RUN wp post term add 4484 category 'Society News'
$RUN wp post term add 4537 category Event
$RUN wp post term add 4537 post_tag Anniversary
$RUN wp post term add 4586 category Event
$RUN wp post term add 4586 category 'Branch News'
$RUN wp post term add 4586 post_tag COBRA-COW
$RUN wp post term add 4586 post_tag Anniversary
$RUN wp post term add 4593 category 'Society News'
$RUN wp post term add 4609 category 'Society News'
$RUN wp post term add 4643 category Event
$RUN wp post term add 4643 post_tag Memorial
$RUN wp post term add 4643 post_tag Walk
$RUN wp post term add 4664 category Event
$RUN wp post term add 4664 post_tag 'Beer and Curry'
$RUN wp post term add 4672 category Event
$RUN wp post term add 4672 post_tag Memorial
$RUN wp post term add 4672 post_tag Walk
$RUN wp post term add 4682 category Event
$RUN wp post term add 4690 category Event
$RUN wp post term add 4690 post_tag Memorial
$RUN wp post term add 4690 post_tag 'Bill English'
$RUN wp post term add 4711 category Event
$RUN wp post term add 4711 post_tag Memorial
$RUN wp post term add 4761 category Event
$RUN wp post term add 4761 category Shop
$RUN wp post term add 4761 post_tag AGM
$RUN wp post term add 4808 category Event
$RUN wp post term add 4808 post_tag Walk
$RUN wp post term add 4829 category Event
$RUN wp post term add 4829 post_tag Memorial
$RUN wp post term add 4847 category Event
$RUN wp post term add 4847 post_tag Walk
$RUN wp post term add 4859 category Event
$RUN wp post term add 4859 post_tag Memorial
$RUN wp post term add 4859 post_tag 'Bill English'
$RUN wp post term add 4902 category Event
$RUN wp post term add 4902 post_tag Walk
$RUN wp post term add 4914 category Event
$RUN wp post term add 4914 category Woodfest
$RUN wp post term add 4914 post_tag Woodfest
$RUN wp post term add 4978 category Pictures
$RUN wp post term add 5017 category Woodfest
$RUN wp post term add 5017 post_tag Woodfest
$RUN wp post term add 5072 category Woodfest
$RUN wp post term add 5072 post_tag Woodfest
$RUN wp post term add 5101 category Woodfest
$RUN wp post term add 5101 category Pictures
$RUN wp post term add 5101 post_tag Woodfest
$RUN wp post term add 5216 category Woodfest
$RUN wp post term add 5216 post_tag Woodfest
$RUN wp post term add 5273 category Event
$RUN wp post term add 5326 category Event
$RUN wp post term add 5326 post_tag Memorial
$RUN wp post term add 5326 post_tag 'Bill English'
$RUN wp post term add 5378 category Event
$RUN wp post term add 5378 post_tag Memorial
$RUN wp post term add 5400 category Event
$RUN wp post term add 5400 post_tag 'National Weekend'
$RUN wp post term add 5511 category Event
$RUN wp post term add 5511 category Pictures
$RUN wp post term add 5511 post_tag Quiz

# 2. Remove 'Uncategorised' from every post that now has a real category.

$RUN wp post term remove 408 category uncategorised
$RUN wp post term remove 414 category uncategorised
$RUN wp post term remove 416 category uncategorised
$RUN wp post term remove 467 category uncategorised
$RUN wp post term remove 1180 category uncategorised
$RUN wp post term remove 1557 category uncategorised
$RUN wp post term remove 1625 category uncategorised
$RUN wp post term remove 1634 category uncategorised
$RUN wp post term remove 1795 category uncategorised
$RUN wp post term remove 1885 category uncategorised
$RUN wp post term remove 1916 category uncategorised
$RUN wp post term remove 1940 category uncategorised
$RUN wp post term remove 1996 category uncategorised
$RUN wp post term remove 2032 category uncategorised
$RUN wp post term remove 2046 category uncategorised
$RUN wp post term remove 2069 category uncategorised
$RUN wp post term remove 2092 category uncategorised
$RUN wp post term remove 2104 category uncategorised
$RUN wp post term remove 2111 category uncategorised
$RUN wp post term remove 2141 category uncategorised
$RUN wp post term remove 2146 category uncategorised
$RUN wp post term remove 2170 category uncategorised
$RUN wp post term remove 2177 category uncategorised
$RUN wp post term remove 3066 category uncategorised
$RUN wp post term remove 3588 category uncategorised
$RUN wp post term remove 3659 category uncategorised
$RUN wp post term remove 3835 category uncategorised
$RUN wp post term remove 4484 category uncategorised
$RUN wp post term remove 4537 category uncategorised
$RUN wp post term remove 4586 category uncategorised
$RUN wp post term remove 4593 category uncategorised
$RUN wp post term remove 4609 category uncategorised
$RUN wp post term remove 4643 category uncategorised
$RUN wp post term remove 4664 category uncategorised
$RUN wp post term remove 4672 category uncategorised
$RUN wp post term remove 4682 category uncategorised
$RUN wp post term remove 4690 category uncategorised
$RUN wp post term remove 4711 category uncategorised
$RUN wp post term remove 4761 category uncategorised
$RUN wp post term remove 4808 category uncategorised
$RUN wp post term remove 4829 category uncategorised
$RUN wp post term remove 4847 category uncategorised
$RUN wp post term remove 4859 category uncategorised
$RUN wp post term remove 4902 category uncategorised
$RUN wp post term remove 4914 category uncategorised
$RUN wp post term remove 4978 category uncategorised
$RUN wp post term remove 5017 category uncategorised
$RUN wp post term remove 5072 category uncategorised
$RUN wp post term remove 5101 category uncategorised
$RUN wp post term remove 5216 category uncategorised
$RUN wp post term remove 5273 category uncategorised
$RUN wp post term remove 5326 category uncategorised
$RUN wp post term remove 5378 category uncategorised
$RUN wp post term remove 5400 category uncategorised
$RUN wp post term remove 5511 category uncategorised

# 3. Check the result.
$RUN wp term list category --fields=name,slug,count
