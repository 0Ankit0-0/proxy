/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(215 20% 20%)',
        input: 'hsl(215 20% 20%)',
        ring: 'hsl(158 100% 50%)',
        background: 'hsl(210 20% 5%)',
        foreground: 'hsl(210 40% 98%)',
        primary: {
          DEFAULT: 'hsl(158 100% 50%)',
          foreground: 'hsl(210 20% 5%)',
        },
        secondary: {
          DEFAULT: 'hsl(210 20% 10%)',
          foreground: 'hsl(210 40% 98%)',
        },
        destructive: {
          DEFAULT: 'hsl(0 84% 60%)',
          foreground: 'hsl(210 40% 98%)',
        },
        muted: {
          DEFAULT: 'hsl(210 20% 10%)',
          foreground: 'hsl(215 20% 65%)',
        },
        accent: {
          DEFAULT: 'hsl(158 100% 50%)',
          foreground: 'hsl(210 20% 5%)',
        },
        popover: {
          DEFAULT: 'hsl(210 20% 7%)',
          foreground: 'hsl(210 40% 98%)',
        },
        card: {
          DEFAULT: 'hsl(210 20% 7%)',
          foreground: 'hsl(210 40% 98%)',
        },
        'command-green': '#00FF88',
        'hazard-yellow': '#FFC300',
        'threat-red': '#FF3B3B',
        'soft-cyan': '#7FD3F5',
        'severity-critical': '#FF3B3B',
        'severity-high': '#FF8C42',
        'severity-medium': '#FFC300',
        'severity-low': '#7FD3F5',
      },
      borderRadius: {
        lg: '8px',
        md: '6px',
        sm: '4px',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [],
}