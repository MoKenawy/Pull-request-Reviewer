import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

// Every id below is a page written to docs/ by scripts/sync-docs.mjs. The order
// follows Docs/developer-documentation-candidates.md, except that the
// level-by-level walkthrough opens the Architecture category.
const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Guides',
      collapsed: false,
      items: ['guides/operation-guide', 'guides/rule-authoring'],
    },
    {
      type: 'category',
      label: 'Architecture',
      collapsed: false,
      items: [
        'architecture/levels',
        'architecture/components',
        'architecture/domain-model',
        'architecture/contract-map',
      ],
    },
    {
      type: 'category',
      label: 'Contracts',
      collapsed: false,
      items: ['contracts/emit-finding', 'contracts/review-report'],
    },
  ],
};

export default sidebars;
