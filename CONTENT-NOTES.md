# Content Notes

The 21 non-home page fragments in `content/pages/` come from the reviewed `outputs/uq-website-draft` version current on 30 September 2026. Their substantive research text is retained. A later layout revision condensed repeated collaboration prompts, linked story titles, and removed decorative arrows; the homepage uses shorter summaries linked to the full pages. The outer WordPress-style shell, draft banner, footer, and navigation were excluded. WordPress block classes were removed; semantic classes, source credits, alt text, links, publication title case, and anchors were preserved.

`content/home-source.html` is a source fragment for the home-page design. Its top “Work with us” and “Saved offline snapshot” links were removed, following the later review. It is not an additional public page.

## Content Checks

- 21 non-home public pages, each with exactly one H1.
- 240 chronological news announcements, plus 125 nested announcement bullets. The 10 year-navigation links are separate.
- 101 entries in the full bibliography.
- 13 selected publications and 9 research stories across 3 themes.
- The SHAP paper is present in the news and full bibliography with the reviewed publication wording. Its title is sentence case, with a capital letter following the colon; no Accepted label or visible DOI was added.
- The Acta Numerica selected-publication thumbnail uses Figure 2.1(a), distinct from the optimal-stopping diagram.
- All referenced local assets and local page targets exist. Internal links remain relative for GitHub project-site hosting.
- All 71 reviewed assets were copied, including font licenses, scientific figure provenance records, sponsor artwork, people, and outings.

## Semantic Layout Hooks

- General page layout: `page-intro`, `wrap`, `section`, `prose`, `intro`, `lead`, `actions`, `button`, `related`, `collab`.
- Research stories: `story-theme`, `story-grid`, `project-card`, `story-thumbnail`, `story-link`.
- Applications: `application-grid`, `application-area`, `application-links`, `application-figure`.
- Publications: `reading-layout`, `publication-list`, `pub pub-illustrated`, `pub-copy`, `publication-title`, `publication-figure`, `pub-links`, `tag`, `meta`, `summary`.
- Story details: `article-body`, `article-figure paper-figure`, `paper-panels`, `panel-label`. Panel containers should accommodate one to three figures without cropping scientific content.
- People: `pi-block`, `people-grid`, `person`.
- Lists: `news-archive`, `news-list`, `archive-years`, `alumni-list`, `topic-list`, `bibliography`. News includes nested lists and stable announcement anchors.
- Contact: `contact-grid`, `contact-address`.
- Teaching: `teaching-course` contains a `course-image` div and a `prose` div.
- Outings: each `outing-gallery` contains figure elements, with no intermediate columns.

## Current Source Limits

People, alumni, teaching histories, and events were preserved as reviewed; no new factual updates were inferred. The space-weather story uses its explicitly dated illustrative forecast and links to the GeoDGP service for current forecasts. The home page has a text-only introduction. Source captions and provenance files should accompany reused scientific figures.


## Owner-Supplied Updates

The SES and IMECE event entries use the presentation details supplied by the site owner. Codie’s portrait and the sponsor artwork have been replaced with the supplied attachments, preserving the original image files. The homepage identifies the group as “Xun Huan · Associate Professor · Mechanical Engineering.”

The header wordmark reads “UQ & SciML,” and the sponsor artwork has a maximum display width of 880 pixels. Each research story’s “The Paper” citation follows the corresponding Full Bibliography entry; existing action buttons provide the paper links.
