{
  "product": {
    "name": "EFUEL Engineering Hub",
    "type": "internal enterprise AI-powered engineering & procurement platform",
    "audience": ["Electrical/EV/Solar engineers", "Procurement teams", "Admins"],
    "north_star": "Fast, trustworthy component decisions with AI-ranked recommendations + defensible citations"
  },
  "brand_personality": {
    "keywords": ["premium", "minimal", "data-dense", "calm", "trustworthy", "engineering-grade"],
    "anti_keywords": ["template-y", "marketing-flashy", "over-gradient", "centered-landing-page"],
    "visual_metaphor": "Precision instrument panel: white lab surface + black anodized hardware + EFUEL blue energy accents"
  },
  "design_tokens": {
    "notes": [
      "Use EFUEL blue as the only strong chroma. Everything else is neutral (white/ink/gray).",
      "Prefer subtle tints for backgrounds; reserve saturated blue for primary actions, links, active states, and key score highlights.",
      "No purple. No saturated gradients. Gradients only as mild decorative overlays <20% viewport."
    ],
    "css_custom_properties": {
      "light": {
        "--background": "0 0% 100%",
        "--foreground": "222 47% 11%",
        "--card": "0 0% 100%",
        "--card-foreground": "222 47% 11%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "222 47% 11%",

        "--primary": "214 92% 52%",
        "--primary-foreground": "0 0% 100%",

        "--secondary": "220 14% 96%",
        "--secondary-foreground": "222 47% 11%",

        "--muted": "220 14% 96%",
        "--muted-foreground": "215 16% 35%",

        "--accent": "214 92% 96%",
        "--accent-foreground": "222 47% 11%",

        "--border": "220 13% 91%",
        "--input": "220 13% 91%",
        "--ring": "214 92% 52%",

        "--destructive": "0 84% 60%",
        "--destructive-foreground": "0 0% 100%",

        "--success": "142 71% 45%",
        "--success-foreground": "0 0% 100%",
        "--warning": "38 92% 50%",
        "--warning-foreground": "222 47% 11%",
        "--info": "199 89% 48%",
        "--info-foreground": "222 47% 11%",

        "--radius": "0.75rem",

        "--shadow-sm": "0 1px 2px rgba(16,24,40,0.06)",
        "--shadow-md": "0 8px 24px rgba(16,24,40,0.10)",
        "--shadow-focus": "0 0 0 4px rgba(59,130,246,0.18)",

        "--sidebar": "220 20% 98%",
        "--sidebar-foreground": "222 47% 11%",
        "--sidebar-active": "214 92% 52%",
        "--sidebar-active-bg": "214 92% 96%"
      },
      "dark": {
        "--background": "222 47% 6%",
        "--foreground": "210 40% 98%",
        "--card": "222 47% 8%",
        "--card-foreground": "210 40% 98%",
        "--popover": "222 47% 8%",
        "--popover-foreground": "210 40% 98%",

        "--primary": "214 92% 60%",
        "--primary-foreground": "222 47% 8%",

        "--secondary": "217 19% 14%",
        "--secondary-foreground": "210 40% 98%",

        "--muted": "217 19% 14%",
        "--muted-foreground": "215 20% 70%",

        "--accent": "214 60% 16%",
        "--accent-foreground": "210 40% 98%",

        "--border": "217 19% 18%",
        "--input": "217 19% 18%",
        "--ring": "214 92% 60%",

        "--destructive": "0 62% 40%",
        "--destructive-foreground": "210 40% 98%",

        "--success": "142 60% 45%",
        "--success-foreground": "222 47% 8%",
        "--warning": "38 92% 55%",
        "--warning-foreground": "222 47% 8%",
        "--info": "199 89% 55%",
        "--info-foreground": "222 47% 8%",

        "--radius": "0.75rem",

        "--shadow-sm": "0 1px 2px rgba(0,0,0,0.35)",
        "--shadow-md": "0 10px 30px rgba(0,0,0,0.45)",
        "--shadow-focus": "0 0 0 4px rgba(96,165,250,0.22)",

        "--sidebar": "222 47% 7%",
        "--sidebar-foreground": "210 40% 98%",
        "--sidebar-active": "214 92% 60%",
        "--sidebar-active-bg": "214 60% 16%"
      }
    },
    "tailwind_usage": {
      "container": "mx-auto w-full max-w-[1440px] px-4 sm:px-6 lg:px-8",
      "page_padding": "py-5 sm:py-6",
      "dense_grid": "grid gap-4 lg:gap-6",
      "card": "rounded-xl border bg-card text-card-foreground shadow-[var(--shadow-sm)]",
      "card_hover": "hover:shadow-[var(--shadow-md)] hover:border-foreground/10",
      "focus_ring": "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
    },
    "gradients_and_texture": {
      "allowed": [
        "Hero/header-only decorative overlay: radial-gradient(1200px circle at 10% 0%, rgba(59,130,246,0.14), transparent 55%), radial-gradient(900px circle at 90% 10%, rgba(14,165,233,0.10), transparent 50%)",
        "Dark mode subtle: radial-gradient(900px circle at 20% 0%, rgba(96,165,250,0.12), transparent 55%)"
      ],
      "noise_overlay_css": ".noise-overlay{position:relative;} .noise-overlay:before{content:'';position:absolute;inset:0;pointer-events:none;background-image:url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22120%22 height=%22120%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22120%22 height=%22120%22 filter=%22url(%23n)%22 opacity=%220.08%22/%3E%3C/svg%3E');mix-blend-mode:overlay;opacity:.35;border-radius:inherit;}"
    }
  },
  "typography": {
    "font_pairing": {
      "display": {
        "name": "Space Grotesk",
        "google_fonts": "https://fonts.google.com/specimen/Space+Grotesk",
        "usage": "H1/H2, key metric numbers, section titles"
      },
      "body": {
        "name": "Inter",
        "google_fonts": "https://fonts.google.com/specimen/Inter",
        "usage": "Body, tables, forms"
      },
      "mono": {
        "name": "IBM Plex Mono",
        "google_fonts": "https://fonts.google.com/specimen/IBM+Plex+Mono",
        "usage": "Part numbers, SKUs, electrical values, tolerances, logs"
      }
    },
    "scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
      "h2": "text-base md:text-lg font-medium text-muted-foreground",
      "section_title": "text-lg font-semibold tracking-tight",
      "card_title": "text-sm font-semibold",
      "body": "text-sm sm:text-base",
      "small": "text-xs text-muted-foreground",
      "numeric": "[font-variant-numeric:tabular-nums]"
    },
    "table_typography": {
      "header": "text-xs font-semibold uppercase tracking-wide text-muted-foreground",
      "cell": "text-sm",
      "mono_cell": "font-mono text-xs sm:text-sm"
    }
  },
  "layout": {
    "app_shell": {
      "structure": [
        "Left: collapsible Sidebar (icon+label, collapses to icon rail)",
        "Top: Header (breadcrumb, global search, quick actions, notifications, profile, theme toggle)",
        "Main: content area with page header + tabs/filters + data region"
      ],
      "sidebar": {
        "width": {"expanded": "w-64", "collapsed": "w-[72px]"},
        "style": "bg-[hsl(var(--sidebar))] text-[hsl(var(--sidebar-foreground))] border-r",
        "nav_item": "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-foreground/5",
        "nav_item_active": "bg-[hsl(var(--sidebar-active-bg))] text-foreground ring-1 ring-[hsl(var(--sidebar-active))]/20",
        "sections": [
          "Core: Dashboard, AI Search, Compare, Component Library, Documents, BOM Builder",
          "AI: AI Assistant",
          "Personal: Favorites, Recent Searches",
          "System: Settings, Admin"
        ]
      },
      "header": {
        "height": "h-14",
        "style": "sticky top-0 z-40 bg-background/80 backdrop-blur border-b",
        "breadcrumb": "Use shadcn breadcrumb; truncate middle segments on mobile",
        "global_search": "Command palette style (shadcn/command) with sources + recent queries"
      },
      "content_grid": {
        "dashboard": "grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6",
        "dashboard_primary": "lg:col-span-8",
        "dashboard_secondary": "lg:col-span-4"
      }
    },
    "responsive_rules": {
      "mobile": [
        "Sidebar becomes Sheet/Drawer (hamburger).",
        "Tables become horizontal ScrollArea with sticky first column OR switch to card-stack for compare.",
        "Header search becomes icon -> opens Command dialog."
      ],
      "desktop": [
        "Keep sidebar visible; allow collapse.",
        "Use resizable panels for Compare and AI Search results (shadcn/resizable)."
      ]
    }
  },
  "components": {
    "component_path": {
      "buttons": "/app/frontend/src/components/ui/button.jsx",
      "cards": "/app/frontend/src/components/ui/card.jsx",
      "tables": "/app/frontend/src/components/ui/table.jsx",
      "forms": "/app/frontend/src/components/ui/form.jsx",
      "inputs": "/app/frontend/src/components/ui/input.jsx",
      "select": "/app/frontend/src/components/ui/select.jsx",
      "tabs": "/app/frontend/src/components/ui/tabs.jsx",
      "accordion": "/app/frontend/src/components/ui/accordion.jsx",
      "dialog": "/app/frontend/src/components/ui/dialog.jsx",
      "drawer_sheet": "/app/frontend/src/components/ui/sheet.jsx",
      "dropdown": "/app/frontend/src/components/ui/dropdown-menu.jsx",
      "command_palette": "/app/frontend/src/components/ui/command.jsx",
      "breadcrumb": "/app/frontend/src/components/ui/breadcrumb.jsx",
      "pagination": "/app/frontend/src/components/ui/pagination.jsx",
      "skeleton": "/app/frontend/src/components/ui/skeleton.jsx",
      "toast": "Use sonner: /app/frontend/src/components/ui/sonner.jsx",
      "tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
      "switch": "/app/frontend/src/components/ui/switch.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "badge": "/app/frontend/src/components/ui/badge.jsx",
      "alert": "/app/frontend/src/components/ui/alert.jsx",
      "calendar": "/app/frontend/src/components/ui/calendar.jsx",
      "scroll_area": "/app/frontend/src/components/ui/scroll-area.jsx",
      "resizable": "/app/frontend/src/components/ui/resizable.jsx"
    },
    "enterprise_patterns": {
      "data_dense_table": {
        "rules": [
          "Sticky header row + subtle row hover.",
          "Use tabular-nums for numeric columns.",
          "Provide density toggle (Condensed/Regular/Relaxed) that changes row padding.",
          "Provide column visibility + export actions in a toolbar.",
          "Use ScrollArea for horizontal overflow; keep first column sticky for identifiers."
        ],
        "row_density_classes": {
          "condensed": "[&_*]:text-xs [&_td]:py-2 [&_th]:py-2",
          "regular": "[&_td]:py-3 [&_th]:py-3",
          "relaxed": "[&_td]:py-4 [&_th]:py-4"
        }
      },
      "ai_search_results": {
        "layout": [
          "Left: results list (ranked top-5) with score badge + vendor + price range.",
          "Right: detail panel with tabs: Overview, Specs, Pros/Cons, Sources, Similar.",
          "Use Resizable panels on desktop; stacked on mobile."
        ],
        "score_visual": "Use a compact gauge: circular progress ring + numeric score + label (Ready/Conditional/Risk)."
      },
      "compare_engine": {
        "max_items": 4,
        "features": [
          "Differences-only toggle.",
          "Pinned key rows (Model, Rating, Poles, Breaking capacity, Standards).",
          "AI winner callout chip per section.",
          "Mobile: each product becomes a card with accordion sections; swipe between products (carousel)."
        ]
      },
      "document_library": {
        "cards": "Use Card + AspectRatio thumbnail + metadata row + actions (Preview, Download, Cite).",
        "preview": "Dialog with embedded PDF viewer area; show skeleton while loading."
      },
      "bom_builder": {
        "table": "Editable table with inline Select for brand, Input for qty, and computed totals.",
        "export": "Primary button: Export CSV/PDF; secondary: Copy to clipboard."
      },
      "ai_assistant": {
        "chat": "Chat layout with message bubbles as Cards; citations as inline Badges; sources open in Drawer.",
        "composer": "Textarea + attachments (PDF) + send button; show streaming indicator skeleton."
      }
    },
    "buttons": {
      "variants": {
        "primary": "bg-primary text-primary-foreground hover:bg-primary/90",
        "secondary": "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        "ghost": "hover:bg-foreground/5",
        "destructive": "bg-destructive text-destructive-foreground hover:bg-destructive/90"
      },
      "shape": "Rounded (8–12px) premium enterprise; avoid pill for primary.",
      "motion": "hover: translateY(-1px) shadow-sm; active: scale-[0.98]"
    },
    "badges_and_status": {
      "engineering_score": {
        "bands": [
          {"range": "80-100", "label": "Ready", "color": "success"},
          {"range": "60-79", "label": "Conditional", "color": "warning"},
          {"range": "0-59", "label": "Risk", "color": "destructive"}
        ],
        "badge_style": "Use Badge with subtle tinted background (accent) + colored dot + numeric score"
      },
      "system_status": "Use Alert for incidents; use Badge for Healthy/Degraded/Down"
    },
    "charts": {
      "library": "recharts",
      "install": "npm i recharts",
      "use_cases": [
        "Price trend sparkline (LineChart)",
        "Score breakdown (BarChart)",
        "Vendor share (PieChart)"
      ],
      "styling": "Use muted gridlines, no heavy fills; highlight active series in primary blue; tooltips in Card/Popover"
    }
  },
  "motion": {
    "library": "framer-motion",
    "principles": [
      "Use motion for state changes: loading->results, sidebar collapse, dialogs, table row expansion.",
      "Prefer opacity + y translate (6-10px) entrance; keep durations 160-220ms.",
      "Avoid animating layout for huge tables; animate only containers and skeleton transitions."
    ],
    "presets": {
      "page_enter": {"initial": "{opacity:0, y:8}", "animate": "{opacity:1, y:0}", "transition": "{duration:0.18, ease:'easeOut'}"},
      "list_stagger": "staggerChildren: 0.04",
      "hover": "whileHover={{ y: -1 }} transition={{ duration: 0.12 }}"
    }
  },
  "accessibility": {
    "rules": [
      "All interactive elements must have visible focus (ring + offset).",
      "Tables must preserve semantic <table> structure.",
      "Color is never the only indicator: pair status colors with labels/icons.",
      "Respect prefers-reduced-motion: disable non-essential animations.",
      "Ensure contrast: body text >= 4.5:1; muted text still readable in dark mode."
    ]
  },
  "testing": {
    "data_testid": {
      "rule": "All interactive and key informational elements MUST include data-testid (kebab-case, role-based).",
      "examples": [
        "data-testid=\"global-search-button\"",
        "data-testid=\"ai-search-input\"",
        "data-testid=\"ai-search-submit-button\"",
        "data-testid=\"ranked-result-row\"",
        "data-testid=\"compare-differences-toggle\"",
        "data-testid=\"theme-toggle\"",
        "data-testid=\"notification-center-button\"",
        "data-testid=\"profile-menu-button\"",
        "data-testid=\"bom-export-csv-button\""
      ]
    }
  },
  "image_urls": {
    "note": "No stock providers available in tool run. Use internal EFUEL assets + simple SVG illustrations.",
    "categories": [
      {
        "category": "background-texture",
        "description": "Use CSS noise overlay + subtle radial blue glow in header only (no large gradients).",
        "urls": []
      },
      {
        "category": "empty-states",
        "description": "Use lightweight inline SVG illustrations (monoline, blueprint style) for: No results, No favorites, No documents.",
        "urls": []
      }
    ]
  },
  "page_blueprints": {
    "auth": {
      "layout": "Split screen: left brand panel (black) with logo + security note; right form card on white.",
      "components": ["card", "form", "input", "select", "button", "separator"],
      "microcopy": "Role selection explains permissions; show SSO placeholder if needed (but do not mock as real)."
    },
    "dashboard": {
      "top": "Quick search + recent searches + system status widgets",
      "middle": "Recommended components + price trend cards",
      "bottom": "Activity feed (recent compares, docs viewed)"
    },
    "ai_search": {
      "states": [
        "Empty: prompt + examples chips",
        "Loading: skeleton + stepper (Searching sources → Extracting specs → Scoring → Ranking)",
        "Results: ranked list + detail panel + citations"
      ]
    },
    "compare": {
      "layout": "Toolbar (add products, differences-only, export) + comparison grid",
      "callouts": "AI winner badge per section + best-value chip"
    },
    "admin": {
      "layout": "Tabs: Users, Brands, Categories, Products, Documents, Logs, API Keys",
      "tables": "Use pagination + column filters + row actions dropdown"
    },
    "404": {
      "tone": "Calm, internal tool: 'This module moved or you don’t have access.'",
      "cta": "Back to Dashboard + Search"
    }
  },
  "instructions_to_main_agent": [
    "Replace CRA default App.css centering styles; do not center the app container.",
    "Update /app/frontend/src/index.css :root and .dark tokens to match EFUEL palette above (blue primary).",
    "Implement AppShell with Sidebar + Header using shadcn components (Sheet for mobile sidebar, DropdownMenu for profile, Command for global search).",
    "Use only existing shadcn components from /src/components/ui for dropdowns, dialogs, calendar, etc.",
    "Implement data-dense tables with sticky headers and ScrollArea; add density toggle.",
    "Add recharts for trends and score breakdown; keep charts minimal and readable.",
    "Every interactive element and key info must include data-testid attributes.",
    "All components are .jsx (TypeScript-style JS). Keep patterns consistent with existing shadcn .jsx files."
  ]
}

---

<General UI UX Design Guidelines>  
    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms
    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text
   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json

 **GRADIENT RESTRICTION RULE**
NEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc
NEVER use dark gradients for logo, testimonial, footer etc
NEVER let gradients cover more than 20% of the viewport.
NEVER apply gradients to text-heavy content or reading areas.
NEVER use gradients on small UI elements (<100px width).
NEVER stack multiple gradient layers in the same viewport.

**ENFORCEMENT RULE:**
    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors

**How and where to use:**
   • Section backgrounds (not content backgrounds)
   • Hero section header content. Eg: dark to light to dark color
   • Decorative overlays and accent elements only
   • Hero section with 2-3 mild color
   • Gradients creation can be done for any angle say horizontal, vertical or diagonal

- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**

</Font Guidelines>

- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. 
   
- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.

- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.
   
- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly
    Eg: - if it implies playful/energetic, choose a colorful scheme
           - if it implies monochrome/minimal, choose a black–white/neutral scheme

**Component Reuse:**
	- Prioritize using pre-existing components from src/components/ui when applicable
	- Create new components that match the style and conventions of existing components when needed
	- Examine existing components to understand the project's component patterns before creating new ones

**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component

**Best Practices:**
	- Use Shadcn/UI as the primary component library for consistency and accessibility
	- Import path: ./components/[component-name]

**Export Conventions:**
	- Components MUST use named exports (export const ComponentName = ...)
	- Pages MUST use default exports (export default function PageName() {...})

**Toasts:**
  - Use `sonner` for toasts"
  - Sonner component are located in `/app/src/components/ui/sonner.tsx`

Use 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.
</General UI UX Design Guidelines>
