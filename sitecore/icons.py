"""
A small, hand-authored inline-SVG icon set used across the site (services, core
values, "why choose us", navigation, socials, etc). Kept dependency-free — no
icon font, no external request — so the design stays fast and fully custom.

Each icon is a 24x24 outline glyph (stroke=currentColor) so it inherits color
and sizing from CSS wherever it's placed.
"""

ICONS = {
    'training': '<path d="M4 19.5V6a2 2 0 0 1 2-2h11l3 3v12.5"/><path d="M4 19.5A1.5 1.5 0 0 0 5.5 21H19a1.5 1.5 0 0 0 1.5-1.5"/><path d="M8 8h8M8 12h8M8 16h4"/>',
    'business': '<path d="M4 21V8l8-4 8 4v13"/><path d="M9 21v-6h6v6"/><path d="M9 12h.01M15 12h.01M12 12h.01M9 8h.01M15 8h.01M12 8h.01"/>',
    'corporate': '<rect x="4" y="3" width="10" height="18" rx="1"/><path d="M14 8h6v13" /><path d="M7 7h.01M7 11h.01M7 15h.01M11 7h.01M11 11h.01M11 15h.01M17 12h.01M17 16h.01"/>',
    'consulting': '<circle cx="12" cy="8" r="3.25"/><path d="M4.5 20.5a7.5 7.5 0 0 1 15 0"/><path d="M17.5 8a3 3 0 1 1 3.4 4.7M6.5 8a3 3 0 1 0-3.4 4.7"/>',
    'target': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="0.75" fill="currentColor" stroke="none"/>',
    'users': '<circle cx="9" cy="8" r="3.25"/><path d="M2.75 20a6.25 6.25 0 0 1 12.5 0"/><path d="M15.5 5.25A3.25 3.25 0 0 1 17 11.4"/><path d="M17.25 14.1a6.25 6.25 0 0 1 4 5.9"/>',
    'spark': '<path d="M12 2.75c.6 3.7 2.55 5.65 6.25 6.25-3.7.6-5.65 2.55-6.25 6.25-.6-3.7-2.55-5.65-6.25-6.25 3.7-.6 5.65-2.55 6.25-6.25Z"/><path d="M19 17.5c.25 1.5 1 2.25 2.5 2.5-1.5.25-2.25 1-2.5 2.5-.25-1.5-1-2.25-2.5-2.5 1.5-.25 2.25-1 2.5-2.5Z"/>',
    'growth': '<path d="M3 20h18"/><path d="M6 20V13M11 20V8M16 20v-6M21 20V4"/>',
    'check': '<path d="M4 12.5 9.5 18 20 6.5"/>',
    'arrow-right': '<path d="M4 12h15.5"/><path d="M13 5.5 19.5 12 13 18.5"/>',
    'phone': '<path d="M6.5 3.5h3l1.5 4.5-2.25 1.75a12 12 0 0 0 5.5 5.5l1.75-2.25 4.5 1.5v3a1.75 1.75 0 0 1-1.9 1.75A16.5 16.5 0 0 1 4.75 5.4 1.75 1.75 0 0 1 6.5 3.5Z"/>',
    'mail': '<rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
    'location': '<path d="M12 21.5s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12Z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="16" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    'award': '<circle cx="12" cy="8.5" r="5.25"/><path d="m8.3 13.2-1.6 7.3 5.3-2.8 5.3 2.8-1.6-7.3"/>',
    'shield': '<path d="M12 2.75 19.5 6v6c0 5-3.2 8.3-7.5 9.75C7.7 20.3 4.5 17 4.5 12V6L12 2.75Z"/><path d="m9 12 2.25 2.25L15.5 9.5"/>',
    'lightbulb': '<path d="M9 18h6M9.75 21.5h4.5"/><path d="M12 2.75A6.25 6.25 0 0 0 8.2 13.9c.9.75 1.3 1.5 1.3 2.6h5c0-1.1.4-1.85 1.3-2.6A6.25 6.25 0 0 0 12 2.75Z"/>',
    'heart': '<path d="M12 20.25S3.75 15.4 3.75 9.4a4.9 4.9 0 0 1 8.25-3.55A4.9 4.9 0 0 1 20.25 9.4c0 6-8.25 10.85-8.25 10.85Z"/>',
    'globe': '<circle cx="12" cy="12" r="9.25"/><path d="M2.75 12h18.5M12 2.75c2.6 2.6 4 5.9 4 9.25s-1.4 6.65-4 9.25c-2.6-2.6-4-5.9-4-9.25s1.4-6.65 4-9.25Z"/>',
    'briefcase': '<rect x="2.75" y="7.5" width="18.5" height="12" rx="1.5"/><path d="M8.5 7.5V5.75a1.5 1.5 0 0 1 1.5-1.5h4a1.5 1.5 0 0 1 1.5 1.5V7.5M2.75 13h18.5"/>',
    'graduation-cap': '<path d="M2.5 9.5 12 5l9.5 4.5-9.5 4.5-9.5-4.5Z"/><path d="M6.5 11.5v4.75c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5V11.5M21.5 9.5v6"/>',
    'megaphone': '<path d="M3 10.5v3a1.5 1.5 0 0 0 1.5 1.5H6l1 5h2l-.7-5h1.2l7 3.5v-12l-7 3.5H4.5A1.5 1.5 0 0 0 3 10.5Z"/>',
    'handshake': '<path d="m2.75 12.5 3.5-3.5a2 2 0 0 1 2.83 0l1.17 1.17M21.25 12.5l-3.5-3.5a2 2 0 0 0-2.83 0L13 10.9"/><path d="m6.25 9 5.75 5.75a1.5 1.5 0 0 0 2.12-2.12l-3.5-3.5M17.75 9l-5.5 5.5"/><path d="m9.25 16.5 1.5 1.5a1.5 1.5 0 0 0 2.12-2.12"/>',
    'chart': '<path d="M4 4v16h16"/><path d="M8 16v-4M12.5 16V7M17 16v-7"/>',
    'star': '<path d="m12 3 2.55 5.85 6.2.6-4.7 4.25 1.35 6.15L12 16.9l-5.4 2.95 1.35-6.15-4.7-4.25 6.2-.6L12 3Z"/>',
    'quote': '<path d="M9.5 6.5c-3 1-5 3.7-5 7.1 0 2.5 1.7 4.4 3.9 4.4a3.4 3.4 0 0 0 3.5-3.5c0-1.9-1.4-3.3-3.2-3.4.35-1.9 1.75-3.35 3.3-3.9L9.5 6.5Zm10 0c-3 1-5 3.7-5 7.1 0 2.5 1.7 4.4 3.9 4.4a3.4 3.4 0 0 0 3.5-3.5c0-1.9-1.4-3.3-3.2-3.4.35-1.9 1.75-3.35 3.3-3.9l-2.5-.7Z" fill="currentColor" stroke="none"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.75"/><path d="m20 20-4.35-4.35"/>',
    'menu': '<path d="M3.5 6.5h17M3.5 12h17M3.5 17.5h17"/>',
    'close': '<path d="m5 5 14 14M19 5 5 19"/>',
    'arrow-up': '<path d="M12 19.5V4.5"/><path d="M5.5 11 12 4.5 18.5 11"/>',
    'chevron-down': '<path d="m5.5 8.5 6.5 6.5 6.5-6.5"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.5l4 2"/>',
    'external-link': '<path d="M9 6H6a1.5 1.5 0 0 0-1.5 1.5V18A1.5 1.5 0 0 0 6 19.5h10.5A1.5 1.5 0 0 0 18 18v-3"/><path d="M14 4h6v6M20 4l-9.5 9.5"/>',
    'building': '<rect x="4.5" y="3" width="9" height="18" rx="1"/><path d="M13.5 9h6v12" /><path d="M8 7h.01M8 11h.01M8 15h.01M17 13h.01M17 17h.01"/>',
    'instagram': '<rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="12" cy="12" r="4"/><circle cx="17.15" cy="6.85" r="1" fill="currentColor" stroke="none"/>',
    'tiktok': '<path d="M14 3.5v11.2a3.1 3.1 0 1 1-2.2-2.97"/><path d="M14 3.5c.3 2.1 1.8 3.7 4 4V10c-1.6 0-3-.5-4-1.4"/>',
    'facebook': '<path d="M14.5 21v-7.5H17l.5-3.2h-3V8.2c0-.9.3-1.5 1.6-1.5H17.6V3.9c-.3 0-1.3-.1-2.4-.1-2.4 0-4 1.45-4 4.1v2.4H8.7v3.2h2.5V21Z" fill="currentColor" stroke="none"/>',
    'linkedin': '<rect x="3.5" y="3.5" width="17" height="17" rx="2.5"/><path d="M8 10v6.5M8 7.25v.01M12.25 16.5V10M12.25 12.75c0-1.6 1-2.75 2.5-2.75s2.75 1 2.75 3v3.5"/>',
    'youtube': '<rect x="2.75" y="5.5" width="18.5" height="13" rx="3.5"/><path d="M10.25 9.25v5.5l4.75-2.75Z" fill="currentColor" stroke="none"/>',
    'whatsapp': '<path d="M6.2 17.8 3.5 20.5l2.75-.7A8.6 8.6 0 1 0 3.5 12a8.5 8.5 0 0 0 1.2 4.4Z"/><path d="M9 9.7c0 3.6 2.7 6.3 6.3 6.3 1 0 1.35-.55 1.35-1.05 0-.4-.2-.6-.55-.85l-1.5-1c-.3-.2-.55-.15-.8.1l-.5.5c-1-.55-1.9-1.4-2.45-2.45l.5-.5c.25-.25.3-.5.1-.8l-1-1.5c-.25-.35-.45-.55-.85-.55-.5 0-1.1.35-1.1 1.3Z" fill="currentColor" stroke="none"/>',
}

ICON_CHOICES = sorted((key, key.replace('-', ' ').title()) for key in ICONS)
