import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const GITHUB = 'https://github.com/MoKenawy/Pull-request-Reviewer';

const config: Config = {
  title: 'agentic-review',
  tagline: 'A local command-line reviewer for TypeScript and JavaScript changes',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Deployment is not set up yet; these are local defaults.
  url: 'https://localhost',
  baseUrl: '/',

  organizationName: 'MoKenawy',
  projectName: 'Pull-request-Reviewer',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // The pages in docs/ are generated from the repository's own Markdown by
  // scripts/sync-docs.mjs. `detect` parses .md files as CommonMark rather than
  // MDX, so JSON examples and `<`/`{` in that prose render as written.
  markdown: {
    format: 'detect',
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },
  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'agentic-review',
      logo: {
        alt: 'agentic-review logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: GITHUB,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Overview', to: '/'},
            {label: 'Operation guide', to: '/guides/operation-guide'},
          ],
        },
        {
          title: 'Specification',
          items: [
            {label: 'SRS v1', href: `${GITHUB}/blob/main/Docs/agentic-code-review-srs-v1.md`},
            {label: 'Technical stack', href: `${GITHUB}/blob/main/Docs/technical_stack.md`},
          ],
        },
        {
          title: 'More',
          items: [{label: 'GitHub', href: GITHUB}],
        },
      ],
      copyright: `Built with Docusaurus from the agentic-review repository.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'python', 'yaml', 'powershell'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
