# ChatLLM — Design System

## 1. Design Objective

ChatLLM is an enterprise application. The visual design should communicate:

```text
Professional
Modern
Trustworthy
Clean
Focused
AI-first
Enterprise-ready
```

The interface should not look like a consumer social application or an overly decorative AI experiment.

---

# 2. Design Direction

Recommended visual direction:

**Modern Enterprise AI**

Use:

- Clean layouts.
- Spacious cards.
- Clear hierarchy.
- Subtle borders.
- Moderate corner radius.
- Strong readability.
- Minimal visual noise.
- Consistent navigation.
- Clear status indicators.

Avoid excessive:

- Gradients.
- Glows.
- Animations.
- Glassmorphism.
- Decorative illustrations.
- Heavy shadows.

---

# 3. Color System

The default ChatLLM theme should use a neutral enterprise base with a controlled blue/violet AI accent.

## Primary

```text
Primary:        #4F46E5
Primary Hover:  #4338CA
Primary Light:  #EEF2FF
```

## Neutral

```text
Background:     #F8FAFC
Surface:        #FFFFFF
Border:         #E2E8F0
Text Primary:   #0F172A
Text Secondary: #475569
Text Muted:     #64748B
```

## Semantic

```text
Success:        #16A34A
Warning:        #D97706
Error:          #DC2626
Info:           #2563EB
```

The final colors can be adjusted after the first UI prototype, but the system should remain consistent.

---

# 4. Dark Mode

Dark mode may be supported later.

Recommended dark palette:

```text
Background:     #0F172A
Surface:        #111827
Surface Alt:    #1E293B
Border:         #334155
Text Primary:   #F8FAFC
Text Secondary: #CBD5E1
Text Muted:     #94A3B8
```

Dark mode should not be treated as a separate design system. It should reuse the same semantic tokens.

---

# 5. Typography

Recommended font:

```text
Inter
```

Fallback:

```text
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Inter is recommended because it is highly readable for dashboards, tables, forms, and chat interfaces.

---

# 6. Typography Scale

```text
Display:        32px / 40px / 700
H1:             28px / 36px / 700
H2:             24px / 32px / 700
H3:             20px / 28px / 600
H4:             18px / 26px / 600

Body Large:     16px / 24px / 400
Body:           14px / 22px / 400
Body Small:     13px / 20px / 400

Label:          13px / 18px / 500
Caption:        12px / 16px / 400
```

---

# 7. Chat Typography

Chat responses should prioritize readability.

```text
User message:
15px / 24px

AI response:
15px / 25px

Code:
13px / 20px
```

Long AI responses should have:

- Paragraph spacing.
- Heading hierarchy.
- Lists.
- Code blocks.
- Tables where appropriate.
- Copy controls where useful.

---

# 8. Layout

Recommended desktop structure:

```text
┌──────────────────────────────────────────────┐
│ Top Bar                                      │
├───────────────┬──────────────────────────────┤
│ Sidebar       │ Main Content                 │
│               │                              │
│ Navigation    │                              │
│               │                              │
└───────────────┴──────────────────────────────┘
```

Employee chat:

```text
┌──────────────┬───────────────────────────────┐
│ Chat History │ Chat Area                     │
│              │                               │
│ Sessions     │ Messages                      │
│              │                               │
│              │ Prompt Input                  │
└──────────────┴───────────────────────────────┘
```

Admin:

```text
Sidebar
  ↓
Dashboard / Users / Roles / Departments /
AI Models / Tokens / Audit / Settings
```

---

# 9. Spacing

Use a consistent spacing scale:

```text
4px
8px
12px
16px
20px
24px
32px
40px
48px
64px
```

Avoid arbitrary spacing values unless required.

---

# 10. Border Radius

Recommended:

```text
Small controls: 6px
Inputs:         8px
Cards:          10px
Dialogs:        12px
Large surfaces: 16px
```

Avoid excessive pill-shaped UI except for:

- Status badges.
- Tags.
- Small categorical controls.

---

# 11. Shadows

Use subtle shadows.

Cards should primarily use:

```text
Border
+
Very subtle shadow where necessary
```

Avoid heavy floating shadows.

---

# 12. Buttons

Primary:

```text
Solid primary color
White text
```

Secondary:

```text
White/neutral background
Border
Dark text
```

Danger:

```text
Error semantic color
```

Buttons must have:

- Hover state.
- Focus state.
- Disabled state.
- Loading state where applicable.

---

# 13. Forms

Forms should be:

- Clear.
- Short where possible.
- Properly labeled.
- Keyboard accessible.
- Validated.
- Consistent.

Never rely only on placeholder text as the label.

---

# 14. Status Design

Use semantic status badges:

```text
Active       → Success
Pending      → Warning
Rejected     → Error
Inactive     → Neutral
Processing   → Info
Failed       → Error
```

Status should not be communicated by color alone. Include text/icon where appropriate for accessibility.

---

# 15. AI Model Selector

The model selector should clearly show:

```text
Provider
Model
Availability
Optional capability
```

Example:

```text
OpenAI
Model Name
Available
```

or:

```text
Anthropic
Model Name
Available
```

The employee should always know which model is being used.

---

# 16. Token Wallet UI

The wallet should clearly display:

```text
Available Tokens
Today's Usage
Daily Allocation
Carry Forward
Bonus
```

Example:

```text
Available
8,500

Used Today
1,500 / 10,000

Carry Forward
2,000

Bonus
500
```

Avoid making token information visually confusing.

---

# 17. Accessibility

Target:

```text
WCAG 2.1 AA
```

Requirements:

- Keyboard navigation.
- Visible focus states.
- Sufficient color contrast.
- Semantic HTML.
- Screen-reader-friendly labels.
- Accessible forms.
- Do not use color as the only status indicator.

---

# 18. Responsive Design

The application must support:

```text
Desktop
Tablet
Mobile
```

Chat is the primary employee workflow, so the mobile chat experience must remain usable.

Admin dashboards can prioritize desktop while remaining responsive.

---

# 19. Animation

Use animation sparingly.

Allowed:

- Loading indicators.
- Modal transitions.
- Sidebar transitions.
- Message appearance.
- Button feedback.

Avoid:

- Constant movement.
- Decorative animations.
- Slow transitions that interfere with productivity.

---

# 20. Design Principle

The interface should make the employee think:

> **"This is my organization's secure AI workspace."**

Not:

> **"This is another consumer chatbot."**
