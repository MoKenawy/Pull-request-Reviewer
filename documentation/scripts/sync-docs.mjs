// Builds documentation/docs/ from the repository's own documents.
//
// The pages are generated, never edited: the sources in Docs/, specs/ and the
// root README stay the only copy. The manifest below mirrors
// Docs/developer-documentation-candidates.md; add a page there first, then here.
// Pages written for this site alone live in documentation/content/ and get the
// same link rewriting.
//
// Run with `npm run sync` (also runs before `start` and `build`).

import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = path.resolve(SITE_DIR, '..');
const DOCS_DIR = path.join(SITE_DIR, 'docs');
const CONTENT_DIR = path.join(SITE_DIR, 'content');
const DIAGRAMS_DIR = path.join(SITE_DIR, 'static', 'img', 'diagrams');
const GITHUB = 'https://github.com/MoKenawy/Pull-request-Reviewer';

// One entry per generated page. `id` is the path under docs/ without `.md`;
// `section` extracts one heading and what sits under it instead of the whole file.
// `omit` maps a heading to the text that replaces it and what sits under it;
// a `doc:<id>` link in that text points at another page of the site.
const PAGES = [
  {id: 'intro', source: 'README.md', title: 'Overview', slug: '/'},
  {id: 'guides/operation-guide', source: 'Docs/operation_guidelines.md', label: 'Operation guide'},
  {id: 'guides/rule-authoring', source: 'Docs/rule-authoring.md', label: 'Writing review rules'},
  {
    id: 'architecture/components',
    source: 'Docs/design/Component-design/README.md',
    label: 'Component design',
    // The site shows the author's own diagrams, one level at a time, on the
    // levels page instead of this redraw of level 3.
    omit: {
      '### 1.1 Level 3':
        'The diagrams themselves are shown one level at a time in the [architecture overview](doc:architecture/levels).',
    },
  },
  {
    id: 'architecture/domain-model',
    source: 'Docs/design/02-domain-model.md',
    section: '## 1 · The map',
    title: 'Domain model: the map',
    label: 'Domain model',
  },
  {
    id: 'architecture/contract-map',
    source: 'Docs/design/schemas-and-contracts.md',
    section: '## 1 · The contract map',
    title: 'Schemas and contracts: the contract map',
    label: 'Contract map',
  },
  {id: 'contracts/emit-finding', source: 'specs/001-walking-skeleton/contracts/emit-finding.md', label: 'emit_finding'},
  {id: 'contracts/review-report', source: 'specs/001-walking-skeleton/contracts/review-report.md', label: 'Review report JSON'},
];

// The component diagrams, shown on content/architecture/levels.md under headings
// that start "Level N". A link to one of them in a source points at its section.
const DIAGRAMS_PAGE = 'architecture/levels';
const DIAGRAMS = [1, 2, 3].map((level) => ({level, source: `Docs/design/Component-design/level-${level}.svg`}));

const toPosix = (p) => p.split(path.sep).join('/');
const blobUrl = (repoPath, anchor = '') => {
  const abs = path.join(REPO_ROOT, repoPath);
  const kind = fs.existsSync(abs) && fs.statSync(abs).isDirectory() ? 'tree' : 'blob';
  return `${GITHUB}/${kind}/main/${repoPath.replace(/\/$/, '')}${anchor}`;
};

// Same algorithm as github-slugger, which Docusaurus uses for heading ids.
const slugify = (text) =>
  text
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}\p{Pc} -]/gu, '')
    .replace(/ /g, '-');

// Yields [line, insideFence] so callers can leave code blocks alone.
function* walk(lines) {
  let fence = null;
  for (const line of lines) {
    const m = line.match(/^ {0,3}(`{3,}|~{3,})/);
    if (fence) {
      yield [line, true];
      if (m && m[1][0] === fence[0] && m[1].length >= fence.length && line.trim() === m[1]) fence = null;
    } else if (m) {
      fence = m[1];
      yield [line, true];
    } else {
      yield [line, false];
    }
  }
}

const headingOf = (line) => line.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/);

// [start, end) of a heading and everything under it, up to the next heading of
// the same or a higher level.
function sectionBounds(source, lines, heading) {
  const marked = [...walk(lines)];
  const start = marked.findIndex(([line, fenced]) => !fenced && line.trim() === heading);
  if (start < 0) throw new Error(`${source}: heading "${heading}" not found`);
  const level = headingOf(heading)[1].length;
  const end = marked.findIndex(([line, fenced], i) => {
    const h = !fenced && i > start && headingOf(line);
    return h && h[1].length <= level;
  });
  return [start, end < 0 ? lines.length : end];
}

function anchorsOf(lines) {
  const anchors = [];
  for (const [line, fenced] of walk(lines)) {
    const h = !fenced && headingOf(line);
    if (h) anchors.push(slugify(h[2]));
  }
  return new Set(anchors);
}

function extract(page) {
  let lines = fs.readFileSync(path.join(REPO_ROOT, page.source), 'utf8').replace(/\r\n/g, '\n').split('\n');
  let title;
  let body;

  for (const [heading, replacement] of Object.entries(page.omit ?? {})) {
    const [start, end] = sectionBounds(page.source, lines, heading);
    // Keep the blank lines and separator that close the omitted section.
    let keepFrom = end;
    while (keepFrom > start + 1 && /^(\s*|-{3,})$/.test(lines[keepFrom - 1])) keepFrom--;
    lines = [...lines.slice(0, start), replacement, ...lines.slice(keepFrom)];
  }

  if (page.section) {
    const [start, end] = sectionBounds(page.source, lines, page.section);
    title = headingOf(page.section)[2];
    body = lines.slice(start + 1, end);
  } else {
    const start = [...walk(lines)].findIndex(([line, fenced]) => !fenced && /^#\s/.test(line));
    title = start >= 0 ? headingOf(lines[start])[2] : page.id;
    body = start >= 0 ? lines.slice(start + 1) : lines;
  }

  // Trailing horizontal rules are section separators in the source, not content.
  while (body.length && /^(\s*|-{3,})$/.test(body.at(-1))) body.pop();
  while (body.length && body[0].trim() === '') body.shift();

  return {...page, title: page.title ?? title, body, anchors: anchorsOf(body)};
}

function rewriteLinks(page, pagesBySource, diagramAnchors) {
  const sourceDir = path.posix.dirname(page.source);
  const pageDir = path.posix.dirname(page.id);
  const docLink = (targetId, anchor) => {
    const rel = path.posix.relative(pageDir, `${targetId}.md`);
    return `${rel.startsWith('.') ? rel : `./${rel}`}${anchor}`;
  };

  const rewrite = (target, isImage) => {
    if (target.startsWith('doc:')) {
      const [id, anchor = ''] = target.slice(4).split(/(?=#)/);
      return docLink(id, anchor);
    }
    if (/^[a-z][a-z0-9+.-]*:/i.test(target)) return target;
    const hashAt = target.indexOf('#');
    const file = hashAt < 0 ? target : target.slice(0, hashAt);
    const anchor = hashAt < 0 ? '' : target.slice(hashAt);

    if (file === '') {
      return page.anchors.has(anchor.slice(1)) ? anchor : blobUrl(page.source, anchor);
    }
    const repoPath = path.posix.normalize(path.posix.join(sourceDir, decodeURI(file)));
    const linked = pagesBySource.get(repoPath);
    if (linked && (anchor === '' || linked.anchors.has(anchor.slice(1)))) return docLink(linked.id, anchor);
    const diagram = DIAGRAMS.find((d) => d.source === repoPath);
    if (diagram && isImage) return `/img/diagrams/level-${diagram.level}.svg`;
    if (diagram) return docLink(DIAGRAMS_PAGE, `#${diagramAnchors.get(diagram.level)}`);
    if (!fs.existsSync(path.join(REPO_ROOT, repoPath))) {
      console.warn(`  warning: ${page.source} links to missing ${repoPath}`);
    }
    return blobUrl(repoPath, anchor);
  };

  const out = [];
  for (const [line, fenced] of walk(page.body)) {
    out.push(
      fenced
        ? line
        : line.replace(
            /(!?)(\[[^\]]*\]\()([^)\s]+)((?:\s+"[^"]*")?\))/g,
            (_, bang, open, target, close) => bang + open + rewrite(target, bang === '!') + close,
          ),
    );
  }
  return out;
}

function frontMatter(fields) {
  const yaml = Object.entries(fields)
    .filter(([, v]) => v !== undefined)
    .map(([k, v]) => `${k}: ${JSON.stringify(v)}`);
  return ['---', ...yaml, '---', ''];
}

function writePage(page, body) {
  const fields = {
    title: page.title,
    sidebar_label: page.label,
    slug: page.slug,
    custom_edit_url: `${GITHUB}/edit/main/${page.source}`,
    ...page.frontMatter,
  };
  // A blockquote, not an admonition: `.md` pages are CommonMark, which has no `:::` syntax.
  const banner = page.local
    ? []
    : [`> **Generated page.** The source is [\`${page.source}\`](${blobUrl(page.source)}). Edit that file, not this page.`, ''];
  const file = path.join(DOCS_DIR, `${page.id}.md`);
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, [...frontMatter(fields), ...banner, ...body, ''].join('\n'));
  console.log(`  ${toPosix(path.relative(SITE_DIR, file))}  <-  ${page.source}`);
}

// Pages under content/ link to repository files by their relative path, like
// any other source, so they also read correctly in an editor's preview and on
// GitHub. Their front matter is flat `key: value` lines.
function contentPages(dir = CONTENT_DIR) {
  return fs.readdirSync(dir, {withFileTypes: true}).flatMap((entry) => {
    const abs = path.join(dir, entry.name);
    if (entry.isDirectory()) return contentPages(abs);
    if (!entry.name.endsWith('.md')) return [];
    let lines = fs.readFileSync(abs, 'utf8').replace(/\r\n/g, '\n').split('\n');
    const frontMatter = {};
    if (lines[0] === '---') {
      const end = lines.indexOf('---', 1);
      for (const line of lines.slice(1, end)) {
        const m = line.match(/^(\w+):\s*(.*)$/);
        if (m) frontMatter[m[1]] = m[2].startsWith('"') ? JSON.parse(m[2]) : m[2];
      }
      lines = lines.slice(end + 1);
    }
    while (lines.length && lines[0].trim() === '') lines.shift();
    while (lines.length && lines.at(-1).trim() === '') lines.pop();
    const source = toPosix(path.relative(REPO_ROOT, abs));
    const id = toPosix(path.relative(CONTENT_DIR, abs)).replace(/\.md$/, '');
    return [{id, source, local: true, frontMatter, body: lines, anchors: anchorsOf(lines)}];
  });
}

function copyDiagrams() {
  fs.mkdirSync(DIAGRAMS_DIR, {recursive: true});
  for (const d of DIAGRAMS) {
    // draw.io embeds the editable diagram in a `content` attribute on <svg>. The
    // page only displays it, and the attribute is long enough that Docusaurus
    // cannot read the image size past it.
    const svg = fs.readFileSync(path.join(REPO_ROOT, d.source), 'utf8');
    fs.writeFileSync(path.join(DIAGRAMS_DIR, `level-${d.level}.svg`), svg.replace(/(<svg\b[^>]*?)\s+content="[^"]*"/, '$1'));
    console.log(`  static/img/diagrams/level-${d.level}.svg  <-  ${d.source}`);
  }
}

// The heading id of each level's section on the levels page.
function diagramHeadings(pages) {
  const levels = pages.find((p) => p.id === DIAGRAMS_PAGE);
  if (!levels) throw new Error(`content/${DIAGRAMS_PAGE}.md not found`);
  return new Map(
    DIAGRAMS.map((d) => {
      const anchor = [...levels.anchors].find((a) => a.startsWith(`level-${d.level}`));
      if (!anchor) throw new Error(`${levels.source}: no heading starting "Level ${d.level}"`);
      return [d.level, anchor];
    }),
  );
}

fs.rmSync(DOCS_DIR, {recursive: true, force: true});
fs.rmSync(DIAGRAMS_DIR, {recursive: true, force: true});
console.log('Syncing developer docs:');

copyDiagrams();
const pages = [...PAGES.map(extract), ...contentPages()];
const pagesBySource = new Map(pages.map((p) => [p.source, p]));
const diagramAnchors = diagramHeadings(pages);
for (const page of pages) {
  writePage(page, rewriteLinks(page, pagesBySource, diagramAnchors));
}
