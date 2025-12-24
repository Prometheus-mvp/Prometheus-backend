Role: Frontend lead.

Task: Create a production-grade React + TypeScript + TailwindCSS (PostCSS) MVP plan and repo structure.

Hard styling rule (non-negotiable):

- Every PAGE file must have a corresponding styles file with the same base name:
  Example: DigestPage.tsx and DigestPage.styles.ts
- Page-specific Tailwind class strings MUST exist only in the page’s .styles.ts file.
- The .tsx page must not contain Tailwind classes inline.
- Shared components may follow the same pattern: Component.tsx + Component.styles.ts

Deliverables:

1. Frontend folder structure:
   - src/pages/\* with Page.tsx + Page.styles.ts
   - src/components/\* with optional Component.styles.ts
   - src/api/ client
   - src/types/
   - src/auth/ (supabase session/jwt)
2. Tooling setup:
   - Tailwind config, postcss.config.js, autoprefixer
   - global css import
   - tsconfig notes
3. Conventions:
   - naming rules for pages/components
   - how styles files export classes (object map)
   - linting/formatting (ESLint + Prettier)
4. Dev scripts + local run instructions

Constraints:

- No design system dependency required.
- All backend API types must be typed (manual in /types OR OpenAPI-generated).
