# UQ–SciML Group Website

An independent static website for the University of Michigan UQ–SciML Group. The site builds with Python's standard library and is ready for GitHub Pages. It does not require WordPress, Node.js, a database, or a paid hosting service.

## Preview Locally

Use Python 3.10 or later. From this directory:

```sh
python3 build.py
python3 verify.py
python3 -m http.server 8767 --bind 127.0.0.1 --directory public
```

Open [the local preview](http://127.0.0.1:8767/). Stop the preview server with Control-C. After editing source files, build again and refresh the browser. Generated files in `public/` are overwritten by the build, so make content changes in the source files below.

## Edit Content and Design

| Location | Purpose |
| --- | --- |
| `content/pages/*.html` | Page text, links, figures, news, and bibliography entries |
| `content/home.html` | Home page layout and introductory content |
| `content/events.html` | Upcoming and interesting events shown on the home page |
| `content/page-meta.json` | Page titles and descriptions |
| `templates/` | Shared page structure and navigation |
| `static/` | Styles, scripts, and other shared files |
| `assets/` | Paper figures, portraits, logos, and local fonts |
| `build.py` | Generates the complete site in `public/` |
| `verify.py` | Checks generated pages and internal links before deployment |
| `.github/workflows/pages.yml` | Builds, verifies, and deploys the site on GitHub |

Keep internal links relative, such as `people.html` or `assets/example.png`. These work both at an account site and under a repository path. Avoid leading slashes such as `/people.html`. Page names are case-sensitive on GitHub Pages.

The workflow obtains the repository's hosting path from GitHub automatically. This path is needed only for the custom 404 page's home link, because a missing page may be requested from any directory. The local build defaults to `/`; a manual build for a repository can use `python3 build.py --base-path /REPOSITORY`.

The build automatically takes the first five announcements from `content/pages/news.html` for the home page. Add new announcements at the top of that archive, and keep older announcements below them. Each announcement needs a unique `id` beginning with `news-`, following the existing entries. Edit upcoming events in `content/events.html`; these remain separate from the news chronology.

Edit the selected papers in `content/pages/publications.html` and the complete record in `content/pages/bibliography.html`. A new story needs a page file, metadata, and a link from `content/pages/stories.html`.

## Paper Downloads

Public paper PDFs are stored in `static/papers/` and published at `papers/`. Link to them with relative addresses such as `papers/huan-2018-compressive-sensing.pdf`. Keep filenames stable so shared download links continue to work. The original source URLs, retrieval dates, page counts, and SHA-256 hashes are recorded in `paper-sources.json`.

The 14 papers formerly linked through Google Drive are bundled with the site. Publisher and arXiv links remain separate. The existing `pdf` and `preprint` labels identify the same versions as before.

The airfoil pressure-tap preprint is also served at `wp-content/uploads/sites/521/2021/02/2020_shzg_aiaa_scitech.pdf` to preserve its former WordPress path after a custom-domain transition. This alias uses the verified Drive copy because the WordPress download was unavailable; byte identity with the old WordPress file is unverified. Keep the alias when replacing or reorganizing that paper.

## Put the Site on GitHub Pages

1. Create a GitHub repository with `main` as its default branch. An ordinary repository gives an address in the form `https://USERNAME.github.io/REPOSITORY/`. A repository named `USERNAME.github.io` gives `https://USERNAME.github.io/`.
2. Copy the **contents of this directory** into the repository root, including the hidden `.github/` directory. The repository root should contain `build.py`, `content/`, `templates/`, `static/`, and `assets/`, rather than another enclosing `uq-github-pages/` directory. Generated `public/` files do not need to be committed.
3. In the repository, open **Settings → Pages → Build and deployment** and set **Source** to **GitHub Actions**.
4. Open **Actions → Build and Deploy GitHub Pages → Run workflow**, and choose `main`. Subsequent pushes to `main` rebuild and deploy automatically.
5. Open the site address shown by the deployment or in **Settings → Pages**.

GitHub Pages is available for public repositories on GitHub Free; private repository availability depends on the account plan. No custom domain or changes to the existing Michigan website are required. [GitHub publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

If the default branch has a different name, update `branches: [main]` in the workflow. The workflow uses GitHub's normal deployment token and does not require a personal access token. It grants deployment permissions only to the deployment job. [GitHub custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

The included workflow has been prepared locally. Running it after the repository has been configured will publish the site.

## Checks and Content Preservation

Run `python3 verify.py` after each build. It checks page titles, descriptions, one primary heading per page, image alternatives, local files and anchors, and relative URL resolution at both account and repository URLs. It also rejects review-only links and WordPress staging addresses.

The verification includes preservation checks for at least 240 news entries and 101 bibliography entries, plus nine research story cards. It also confirms that the home page contains the archive's first five announcements. These are the records included in this version; adding news or publications is allowed. Update the story-count constant in `verify.py` if the research story collection is intentionally expanded. External publisher and project URLs are not checked for availability.

## Sources and Rights

Scientific figures retain their paper links and captions. Asset source records and bundled font license files are retained with the assets. Publication figures, photographs, university marks, sponsor logos, and fonts may have their own rights and terms. No blanket license is assigned to those materials or to the new site source code; the site owner can choose an appropriate source-code license separately.

The live GeoDGP image is supplied by its external project. Its availability depends on that service; the site includes a local fallback image.

The workflow action versions were checked against the official action releases when this package was prepared: [checkout](https://github.com/actions/checkout/releases), [setup-python](https://github.com/actions/setup-python/releases), [configure-pages](https://github.com/actions/configure-pages/releases), [upload-pages-artifact](https://github.com/actions/upload-pages-artifact/releases), and [deploy-pages](https://github.com/actions/deploy-pages/releases).
